# -*- coding: utf-8 -*-

import logging
import time

import dask.array as da
from iris.analysis import Aggregator
import iris.coords

from .dask_setup import progress
from .util import change_units
from .datahandling import configure_global_attributes_output


class PointLocalAggregator(Aggregator):
    def __init__(self, index_function, output_metadata, **kwargs):
        self.index_function = index_function
        self.output_metadata = output_metadata
        super().__init__(
            cell_method=None,
            call_func=self.index_function.call_func,
            lazy_func=self.index_function.lazy_func,
            **kwargs,
        )

    def update_metadata(self, cube, coords, **kwargs):
        super().update_metadata(cube, coords, **kwargs)
        cube.var_name = self.output_metadata.var_name
        cube.long_name = self.output_metadata.long_name
        cube.standard_name = self.index_function.standard_name
        cube.units = self.index_function.units
        cube.cell_methods = tuple(
            [
                iris.coords.CellMethod(cm.method, cm.name)
                for cm in self.output_metadata.cell_methods
            ]
        )

    def compute_pre_result(self, data, client, sliced_mode):
        if sliced_mode:
            logging.debug("Computing pre-result in sliced mode")
            stack = []
            end = time.time()
            cumulative = 0.0
            no_slices = len(data)
            for i, d in enumerate(data):
                result_id = f"{i+1}/{no_slices}"
                logging.info(f"Computing partial pre-result {result_id}")
                d = client.persist(d)
                progress(d)
                print()
                stack.append(d)
                start = end
                end = time.time()
                last = end - start
                cumulative += last
                eta = cumulative / (i + 1) * no_slices
                logging.info(
                    f"Finished {result_id} in (last cum eta): "
                    f"{last:4.0f} {cumulative:4.0f} {eta:4.0f}"
                )
            data = da.stack(stack, axis=0)
        else:
            logging.debug("Setting up pre-result in aggregate mode")
            start = time.time()
            data = client.persist(data)
            end = time.time()
            logging.debug(f"Setup completed in {end - start:4.0f}")
        return data

    def post_process(self, cube, data, coords, client, sliced_mode, **kwargs):
        data = self.compute_pre_result(data, client, sliced_mode)
        try:
            post_processor = self.index_function.post_process
        except AttributeError:
            # this index function does not require post processing
            pass
        else:
            cube, data = post_processor(cube, data, coords, **kwargs)
        cube = super().post_process(cube, data, coords, **kwargs)
        standard_name = self.output_metadata.standard_name
        unit_standard_name = standard_name
        proposed_standard_name = self.output_metadata.proposed_standard_name
        if unit_standard_name is None:
            unit_standard_name = proposed_standard_name
        change_units(cube, self.output_metadata.units, unit_standard_name)
        cube.standard_name = standard_name
        if proposed_standard_name is not None:
            cube.attributes["proposed_standard_name"] = proposed_standard_name
        for extra_coord in self.index_function.extra_coords:
            cube.add_aux_coord(extra_coord)
        configure_global_attributes_output(
            cube, kwargs.get("climix_config"), kwargs.get("distribution")
        )
        return cube

    def pre_aggregate_shape(self, *args, **kwargs):
        return self.index_function.pre_aggregate_shape(*args, **kwargs)
