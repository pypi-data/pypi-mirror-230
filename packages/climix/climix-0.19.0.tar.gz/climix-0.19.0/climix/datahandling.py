# -*- coding: utf-8 -*-

import logging
import time

from datetime import datetime
import iris
import iris.config
import netCDF4
import numpy as np
from dask.distributed import wait
from iris.util import equalise_attributes
from iris.fileformats.netcdf import CF_CONVENTIONS_VERSION

from .dask_setup import progress
from .util import find_cube_differences
from . import __version__

logger = logging.getLogger(__name__)


#: Constant that is used to indicate missing value.
MISSVAL = 1.0e20


def get_output_configuration_attributes(cubes, attributes, distribution):
    """Returns a dict with all attributes defined in the configuration"""
    fill_value = {
        "NOW": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S UTC"),
        "CLIMIX_VERSION": f"Climix-{__version__}",
        "INDEX_DISTRIBUTION": (
            f"{distribution.name}-{distribution.version}"
            if distribution is not None and distribution.name is not None
            else ""
        ),
        "CF_CONVENTIONS_VERSION": f"{CF_CONVENTIONS_VERSION}",
    }
    fill_value.update(cubes[0].attributes)
    attribute_dict = {}
    for attribute_config in attributes:
        attr_name = attribute_config.attr_name
        attr_value = attribute_config.attribute
        if attr_value:
            attribute_dict[attr_name] = attr_value.format(**fill_value)
        else:
            raise ValueError(f"Attribute value could not be found for <{attr_name}>")
    return attribute_dict


def configure_global_attributes_output(cube, climix_config=None, distribution=None):
    """Applies global attribute output configurations to all cubes"""
    if climix_config is not None:
        logging.info("Applying global attribute output configuration")
        cubes = [cube]
        output_configuration = climix_config["global_attributes"].output
        attributes = get_output_configuration_attributes(
            cubes, output_configuration.create, distribution
        )
        replaced_attributes = add_global_attributes(cubes, attributes)
        if replaced_attributes:
            logging.debug(f"Following attributes were replaced: {replaced_attributes}")


def drop_unspecified_global_attributes(cubes, config):
    """
    Drops all unspecified global attributes for all cubes and returns a list with
    removed attributes
    """
    attributes_to_keep = [attribute.attr_name for attribute in config.transfer]
    all_attributes = set()
    for cube in cubes:
        all_names = [
            attr_name
            for attr_name in cube.attributes
            if attr_name not in attributes_to_keep
        ]
        all_attributes.update(all_names)
    removed_attributes = drop_global_attributes(cubes, list(all_attributes))
    return removed_attributes


def equalize_global_attributes(cubes):
    """
    Remove attributes that are different between cubes and returns a list with
    removed attributes
    """
    removed_attributes = equalise_attributes(cubes)
    unique_attributes = set()
    for attribute in removed_attributes:
        if isinstance(attribute, dict):
            for attr_name, attr_value in attribute.items():
                unique_attributes.add(f"{attr_name} = {attr_value}")
    return list(unique_attributes)


def default_configuration(cubes, config):
    """
    Applies default configuration to all cubes and returns a list with removed
    attributes
    """
    removed_attributes = []
    if config.default == "drop":
        removed_attributes = drop_unspecified_global_attributes(cubes, config)
    return removed_attributes


def drop_global_attributes(cubes, attributes):
    """
    Drops global attributes specified in a list for all cubes and returns a list with
    removed attributes
    """
    removed_attributes = set()
    if attributes:
        for cube in cubes:
            for attr_name in attributes:
                if attr_name in cube.attributes:
                    attr_value = cube.attributes.pop(attr_name, None)
                    removed_attributes.add(f"{attr_name} : {attr_value}")
    return list(removed_attributes)


def add_global_attributes(cubes, attributes):
    """
    Add global attributes from a dictionary to all cubes and return a list with
    replaced attributes
    """
    replaced_attributes = set()
    if attributes:
        for cube in cubes:
            for attr_name, attr_value in attributes.items():
                if (
                    attr_name in cube.attributes
                    and attr_value != cube.attributes[attr_name]
                ):
                    replaced_attributes.add(
                        f"{attr_name} = {cube.attributes[attr_name]}"
                    )
                cube.attributes[attr_name] = attr_value
    return list(replaced_attributes)


def join_global_attribute_values(cubes, attr_names):
    """
    Returns a list with joined attribute values and a list with attributes that could
    not be found in all cubes.
    """
    attr_values_to_join = set()
    attributes_not_found = set()
    for cube in cubes:
        attr_values = []
        for attr_name in attr_names:
            if attr_name in cube.attributes:
                attr_values.append(cube.attributes[attr_name])
            else:
                attributes_not_found.add(attr_name)
        if attr_values:
            attr_values_to_join.add("_".join(attr_values))
    return list(attr_values_to_join), list(attributes_not_found)


def get_input_configuration_attributes(cubes, transfer):
    """
    Returns a dict with all transfer attributes defined in the configuration and a list
    with attributes that could not be found in all cubes.
    """
    attribute_dict = {}
    attributes_not_found = set()
    for attribute_config in transfer:
        attr_name = attribute_config.attr_name
        if attribute_config.attributes:
            attr_values, attr_not_found = join_global_attribute_values(
                cubes, attribute_config.attributes
            )
        else:
            raise ValueError(f"Attributes could not be found for <{attr_name}>")
        attributes_not_found.update(attr_not_found)
        if attr_values:
            attribute_dict[attr_name] = ", ".join(attr_values)
    return attribute_dict, list(attributes_not_found)


def configure_global_attributes_input(cubes, climix_config=None):
    """Applies global attribute input configurations to all cubes"""
    removed_attributes = set()
    if (climix_config is not None) and ("global_attributes" in climix_config):
        logging.info("Applying global attribute input configuration")
        input_configuration = climix_config["global_attributes"].input
        transfer, attr_not_found = get_input_configuration_attributes(
            cubes, input_configuration.transfer
        )
        if attr_not_found:
            logging.debug(
                "Following attributes were not found in all cubes: "
                f"{list(attr_not_found)}"
            )
        replaced_attributes = add_global_attributes(cubes, transfer)
        if replaced_attributes:
            logging.debug(f"Following attributes were replaced: {replaced_attributes}")
        if input_configuration.drop:
            removed_attr = drop_global_attributes(cubes, input_configuration.drop)
            removed_attributes.update(removed_attr)
        if input_configuration.default:
            removed_attr = default_configuration(cubes, input_configuration)
            removed_attributes.update(removed_attr)
    removed_attr = equalize_global_attributes(cubes)
    removed_attributes.update(removed_attr)
    if removed_attributes:
        logging.debug(
            f"Attributes were removed to equalize cubes: <{list(removed_attributes)}>."
        )


def prepare_input_data(datafiles, climix_config=None):
    """
    Produce a :class:`iris.cube.CubeList` containing cubes for the given data.

    This loads the data from all the given files and merges them into one cube
    per variable. In the process, there might be potentially conflicting global
    attributes that cannot be merged. To transfer global attributes there is a
    default climix configuration file which can be used. If no configuration is
    given, the content of the cubes will be equalized by removing the attributes
    that conflict. If the given `datafiles` cannot be concatenated into a single
    cube per variable, the function raises a :exc:`ValueError`.

    Parameters
    ----------
    datafiles : list of string
        A list of paths to datafiles.
    climix_config : GlobalAttributesConfiguration
        A GlobalAttributesConfiguration object that contains the configuration for
        input and output global attributes.

    Returns
    -------
    cubes : iris.cube.CubeList
        A list of cubes, one per variable, referencing the corresponding data
        from all the passed data files.

    Raises
    ------
    ValueError
        If the given data can not be concatenated into one cube per variable.
        In this case, it is advised to investigate the problem by loading the
        same set of files in an interactive session with iris. Additionally a
        description is printed of the differences found when comparing the
        cubes variables, 'global' attributes, and coordinates.
    """
    datacubes = iris.load_raw(datafiles)
    iris.util.unify_time_units(datacubes)
    configure_global_attributes_input(datacubes, climix_config)
    cubes = datacubes.concatenate()
    var_names = [c.var_name for c in cubes]
    if len(var_names) > len(set(var_names)):  # noqa
        cubes_per_var_name = {}
        for c in cubes:
            cs = cubes_per_var_name.setdefault(c.var_name, [])
            cs.append(c)
        inconsistent_var_names = []
        for var_name, cubes in cubes_per_var_name.items():
            if len(cubes) > 1:
                logging.info(
                    f"Found too many cubes for variable <{var_name}>. Running "
                    "<find_cube_differences>."
                )
                inconsistent_var_names.append(var_name)
                find_cube_differences(cubes, oper="VGC", return_type="logging")
        raise ValueError(
            "Found too many cubes for var_names {}. "
            "See log for details.".format(inconsistent_var_names)
        )
    for c in cubes:
        time = c.coord("time")
        if not time.has_bounds():
            time.guess_bounds()
    return cubes


def save(
    result,
    output_filename,
    iterative_storage=False,
    client=None,
    conventions_override=False,
):
    """
    Save the result cube to the given output file.

    If there are outstanding computations in lazy data in the cube, this
    function realizes the results, i.e. performs all outstanding computations,
    loading the input data into memory. To avoid memory problems, we offer two
    different approaches on how this is done:

    If `iterative_storage` is `True`, first an empty cube is saved, putting all
    metadata and coordinates in place, then the result is realized and stored
    one timeslice at a time, sequentially. This potentially reduces
    parallelism, but also reduces memory requirements. Furthermore, it means
    that on unplanned termination, all finished calculations are already
    stored.

    If `iterative_storage` is `False`, the complete result is realized first,
    maximizing the parallel use of the cluster as exposed by `client`, but
    potentially leading to memory problems if there are large intermediate
    results. This also means that all results are lost in the case of unplanned
    termination.

    Parameters
    ----------
    result : iris.cube.Cube
        The iris cube to be saved.
    output_filename : string
        The filename of the output. Must refer to a netCDF4 file.
    iterative_storage : bool
        Whether to perform iterative storage (see above).
    client : distributed.Client
        The :class:`distributed.Client` object giving access to the cluster.
    """
    data = result.core_data().rechunk()
    if iterative_storage:
        logger.info("Storing iteratively")
        logger.debug("Creating empty data")
        result.data = np.zeros(data.shape, data.dtype)
        # Touch coord data to realize before save
        for coord in result.coords():
            coord.points
            coord.bounds
        logger.debug("Saving empty cube")
        with iris.config.netcdf.context(conventions_override=conventions_override):
            iris.save(
                result,
                output_filename,
                fill_value=MISSVAL,
                local_keys=["proposed_standard_name"],
            )
        logger.debug("Reopening output file and beginning storage")
        with netCDF4.Dataset(output_filename, "a") as ds:
            var = ds[result.var_name]
            time_dim = result.coord_dims("time")[0]
            no_slices = result.shape[time_dim]

            end = time.time()
            cumulative = 0.0
            start_index = 0
            for result_data in data.blocks:
                result_id = f"{start_index+1}/{no_slices}"
                logger.info(f"Storing partial result {result_id}")
                end_index = start_index + result_data.shape[0]
                logger.debug(f"{start_index}:{end_index}")
                logger.debug(f"{result_data.shape}")
                result_data = client.compute(result_data)
                wait(result_data)
                result_data = result_data.result()
                var[start_index:end_index, ...] = result_data
                start_index = end_index
                start = end
                end = time.time()
                last = end - start
                cumulative += last
                eta = cumulative / (start_index + 1) * no_slices
                logger.info(
                    f"Finished {result_id} in (last cum eta): "
                    f"{last:4.0f} {cumulative:4.0f} {eta:4.0f}"
                )
    else:
        logger.info("Storing non-iteratively")
        logger.debug("Computing result")
        r = client.compute(data)
        progress(r)
        print()
        result.data = r.result()
        # Touch coord data to realize before save
        for coord in result.coords():
            coord.points
            coord.bounds
        logger.debug("Storing result")
        with iris.config.netcdf.context(conventions_override=conventions_override):
            iris.save(
                result,
                output_filename,
                fill_value=MISSVAL,
                local_keys=["proposed_standard_name"],
            )
    logger.debug("Calculation complete")
