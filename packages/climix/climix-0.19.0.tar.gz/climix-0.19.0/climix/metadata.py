# -*- coding: utf-8 -*-

from dataclasses import dataclass
import copy
from enum import Enum
import glob
from itertools import combinations
import logging
import os
import re
import string
import sys
from typing import Any, List, Mapping, Union

import iris
import xdg.BaseDirectory
import yaml

from .index import Index
from .period import PeriodSpecification


if sys.version_info[:2] >= (3, 10):
    # pylint: disable=no-name-in-module
    from importlib.metadata import entry_points
else:
    from importlib_metadata import entry_points


@dataclass(eq=True, frozen=True)
class Distribution:
    name: str
    version: str


@dataclass
class CellMethod:
    name: str
    method: str


def format_var_name(var_name, parameters):
    def format_value(value):
        if value < 0:
            return f"m{-value}"
        else:
            return f"{value}"

    parsed_var_name = list(string.Formatter().parse(var_name))
    items = {
        ft[1]: format_value(parameters[ft[1]])
        for ft in parsed_var_name
        if ft[1] is not None
    }
    return var_name.format(**items)


@dataclass
class OutputVariable:
    var_name: str
    standard_name: str
    proposed_standard_name: str
    long_name: str
    units: str
    cell_methods: List[CellMethod]

    @property
    def drs(self):
        return {"var_name": self.var_name}

    def instantiate(self, parameters):
        return OutputVariable(
            format_var_name(self.var_name, parameters),
            self.standard_name,
            self.proposed_standard_name,
            self.long_name.format(**parameters),
            self.units,
            self.cell_methods,
        )


@dataclass
class InputVariable:
    var_name: str
    standard_name: str
    cell_methods: List[CellMethod]
    aliases: List[str]

    def instantiate(self, parameters):
        return InputVariable(
            format_var_name(self.var_name, parameters),
            self.standard_name,
            self.cell_methods,
            self.aliases,
        )


def build_variable(name, variable, path):
    cell_methods = [CellMethod(*cm.popitem()) for cm in variable.pop("cell_methods")]
    return InputVariable(
        name, variable["standard_name"], cell_methods, variable["aliases"]
    )


class ParameterKind(Enum):
    FLAG = "flag"
    OPERATOR = "operator"
    QUANTITY = "quantity"
    REDUCER = "reducer"
    TIME_RANGE = "time_range"


PARAMETER_KINDS = {}


@dataclass
class ParameterFlag:
    name: str
    flag: bool
    kind: ParameterKind = ParameterKind.FLAG

    @property
    def parameter(self):
        return self.flag

    def instantiate(self, parameters):
        return ParameterFlag(ParameterKind.FLAG, self.flag)


PARAMETER_KINDS["flag"] = ParameterFlag


@dataclass
class ParameterOperator:
    name: str
    operator: str
    kind: ParameterKind = ParameterKind.OPERATOR

    @property
    def parameter(self):
        return self.operator

    def instantiate(self, parameters):
        return ParameterOperator(ParameterKind.OPERATOR, self.operator)


PARAMETER_KINDS["operator"] = ParameterOperator


@dataclass
class ParameterQuantity:
    var_name: str
    standard_name: str
    data: Any
    units: str
    long_name: str = None
    proposed_standard_name: str = None
    kind: ParameterKind = ParameterKind.QUANTITY

    @property
    def parameter(self):
        return iris.coords.AuxCoord(
            self.data,
            self.standard_name,
            self.long_name,
            self.var_name,
            units=self.units,
        )

    def instantiate(self, parameters):
        data = self.data
        if isinstance(data, dict) and len(data) == 1:
            key, value = data.popitem()
            data = parameters[key]
        elif isinstance(data, str):
            data = int(data.format(**parameters))
        ln = self.long_name
        if ln is not None:
            ln = ln.format(**parameters)
        param = ParameterQuantity(
            format_var_name(self.var_name, parameters),
            self.standard_name,
            data,
            self.units,
            ln,
        )
        return param


PARAMETER_KINDS["quantity"] = ParameterQuantity


@dataclass
class ParameterReducer:
    name: str
    reducer: str
    kind: ParameterKind = ParameterKind.REDUCER

    @property
    def parameter(self):
        return self.reducer

    def instantiate(self, parameters):
        return ParameterReducer(ParameterKind.REDUCER, self.reducer)


PARAMETER_KINDS["reducer"] = ParameterReducer


@dataclass
class ParameterTimeRange:
    name: str
    data: str
    kind: ParameterKind = ParameterKind.TIME_RANGE

    @property
    def parameter(self):
        return self.data

    def instantiate(self, parameters):
        return ParameterTimeRange(ParameterKind.TIME_RANGE, self.data)


PARAMETER_KINDS["time_range"] = ParameterTimeRange


Parameter = Union[
    ParameterQuantity, ParameterOperator, ParameterReducer, ParameterTimeRange
]


@dataclass
class IndexFunction:
    name: str
    parameters: Mapping[str, Parameter]

    def instantiate(self, parameters):
        return IndexFunction(
            self.name,
            {
                name: param.instantiate(parameters)
                for name, param in self.parameters.items()
            },
        )


@dataclass
class IndexDefinition:
    reference: str
    default_period: str
    output: OutputVariable
    input: Mapping[str, InputVariable]
    index_function: IndexFunction
    source: str
    distribution: Distribution

    def instantiate(self, parameters):
        idx = IndexDefinition(
            self.reference,
            self.default_period,
            self.output.instantiate(parameters),
            {key: iv.instantiate(parameters) for key, iv in self.input.items()},
            self.index_function.instantiate(parameters),
            self.source,
            self.distribution,
        )
        return idx


def build_parameter(name, metadata):
    return PARAMETER_KINDS[metadata["kind"]](name, **metadata)


def build_index(metadata, variables, source=None, distribution=None):
    if (cell_methods := metadata["output"]["cell_methods"]) is None:  # noqa
        cms = []
    else:
        cms = [CellMethod(*cm.popitem()) for cm in cell_methods]
    output = OutputVariable(
        metadata["output"]["var_name"],
        metadata["output"]["standard_name"],
        metadata["output"].get("proposed_standard_name", None),
        metadata["output"]["long_name"],
        metadata["output"]["units"],
        cms,
    )
    if isinstance(metadata["input"], str):
        input_metadata = {"data": metadata["input"]}
    else:
        input_metadata = metadata["input"]
    input = {key: variables[name] for key, name in input_metadata.items()}
    params = metadata["index_function"]["parameters"]
    if params is None:
        parameters = {}
    else:
        parameters = {name: build_parameter(name, params[name]) for name in params}
    index_function = IndexFunction(metadata["index_function"]["name"], parameters)
    idx = IndexDefinition(
        metadata["reference"],
        metadata["default_period"],
        output,
        input,
        index_function,
        source,
        distribution,
    )
    return idx


def get_signature_candidates(signature_parts):
    m_indices = [i for i, p in enumerate(signature_parts) if p.endswith("m")]
    combs = sum(
        [list(combinations(m_indices, i)) for i in range(len(m_indices) + 1)], []
    )
    candidates = []
    for combination in combs:
        parts = copy.copy(signature_parts)
        for idx in combination:
            parts[idx] = parts[idx][:-1]
        candidates.append(tuple(parts))
    return zip(combs, candidates)


class IndexCatalog:
    def __init__(self, indices):
        self.indices = indices
        self._build_template_index()

    def get_list(self):
        return self.indices.keys()

    def _build_template_index(self):
        expr = re.compile(r"{([^}]+)}")
        template_index = {}
        for index in self.indices.keys():
            split = expr.split(index)
            if len(split) == 1:
                continue
            signature = tuple(split[::2])
            parameter_names = split[1::2]
            template_index[signature] = (index, parameter_names)
        self.template_index = template_index

    def get_index_definition(self, index):
        try:
            return self.indices[index]
        except KeyError:
            index_expr = re.compile(r"(\d+)")
            split = index_expr.split(index)
            if len(split) == 1:
                raise
            signature_parts = split[::2]
            candidates = get_signature_candidates(signature_parts)
            matching_signatures = [
                candidate
                for candidate in candidates
                if candidate[1] in self.template_index
            ]
            if len(matching_signatures) == 0:
                raise
            elif len(matching_signatures) > 1:
                raise RuntimeError("More than one matching signature found")
            combination, signature = matching_signatures[0]
            template_name, parameter_names = self.template_index[signature]
            parameter_values = split[1::2]
            for i in combination:
                parameter_values[i] = "-" + parameter_values[i]
            parameter_dict = {
                name: int(value)
                for (name, value) in zip(parameter_names, parameter_values)
            }
            template = self.indices[template_name]
            index_definition = template.instantiate(parameter_dict)
            return index_definition

    def prepare_indices(self, requested_indices, period=None, reference_period=None):
        def select_period(period_string):
            period_parts = period_string.split("[")
            period_type = period_parts[0]
            if len(period_parts) == 2 and period_parts[1][-1] == "]":
                parameters = period_parts[1][:-1]
            else:
                parameters = None
            return PeriodSpecification(period_type, parameters)

        indices = []
        for index_name in requested_indices:
            definition = self.get_index_definition(index_name)
            period_spec = select_period(
                definition.default_period if period is None else period
            )
            if reference_period is not None:
                if "reference_period" not in definition.index_function.parameters:
                    logging.warning(
                        f"Trying to apply a reference period to index <{index_name}>, "
                        f"but <{index_name}> doesn't use it."
                    )
                else:
                    definition.index_function.parameters[
                        "reference_period"
                    ].data = reference_period
            try:
                index_function = build_index_function(definition.index_function)
            except TypeError:
                logging.error(
                    f"Could not build index function for index "
                    f"{index_name} from definition {definition}"
                )
                raise
            logging.info(
                f"Trying to build index <{index_name}> "
                f"with period <{period_spec.type}"
                f"({p if (p := period_spec.parameters) is not None else ''})> "
                f"from definition in <{definition.distribution.name}-"
                f"{definition.distribution.version}> ({definition.source})."
            )
            index = Index(index_function, definition, period_spec)
            indices.append(index)
        return indices


def build_index_function(spec):
    name = spec.name
    candidates = list(entry_points(group="climix.index_functions", name=name))
    if len(candidates) == 0:
        raise ValueError(f"No implementation found for index_function <{name}>")
    elif len(candidates) > 1:
        distributions = [candidate.dist for candidate in candidates]
        raise ValueError(
            f"Found several implementations for index_function <{name}>. "
            f"Please make sure only one is installed at any time. "
            f"The implementations come from the distributions {distributions}"
        )
    candidate = candidates[0]
    logging.info(
        f"Found implementation for index_function <{name}> "
        f"from distribution <{candidate.dist}>"
    )
    index_function_factory = candidates[0].load()
    parameters = {name: param.parameter for name, param in spec.parameters.items()}
    index_function = index_function_factory(**parameters)
    return index_function


def build_distribution(metadata):
    dist_metadata = metadata.get("distribution", {})
    return Distribution(dist_metadata.get("name"), dist_metadata.get("version"))


@dataclass
class InputTransferConfiguration:
    attr_name: str
    attributes: List[str]


@dataclass
class OutputCreateConfiguration:
    attr_name: str
    attribute: str


@dataclass
class GlobalAttributesInputConfiguration:
    default: str = None
    drop: List[str] = None
    transfer: InputTransferConfiguration = None


@dataclass
class GlobalAttributesOutputConfiguration:
    create: OutputCreateConfiguration = None


@dataclass
class GlobalAttributesConfiguration:
    input: GlobalAttributesInputConfiguration
    output: GlobalAttributesOutputConfiguration


def build_global_attr_config(metadata, source=None):
    """Constructs the global attribute configuration from the configuration metadata"""
    input_transfer = []
    output_create = []
    if metadata["input"]["transfer"]:
        for attr_name, attributes in metadata["input"]["transfer"].items():
            input_transfer.append(InputTransferConfiguration(attr_name, attributes))
    if metadata["output"]["create"]:
        for attr_name, attribute in metadata["output"]["create"].items():
            output_create.append(OutputCreateConfiguration(attr_name, attribute))
    input = GlobalAttributesInputConfiguration(
        metadata["input"]["default"],
        metadata["input"]["drop"],
        input_transfer,
    )
    output = GlobalAttributesOutputConfiguration(
        output_create,
    )
    global_attribute_configuration = GlobalAttributesConfiguration(
        input,
        output,
    )
    return global_attribute_configuration


def find_metadata_files_in_dir(directory):
    if os.path.isdir(directory):
        return glob.glob(os.path.join(directory, "*.yml"))
    return []


def find_metadata_files(metadata_files):
    directories = [
        os.path.join(os.path.dirname(__file__), "etc"),
        "/etc/climix",
    ] + list(xdg.BaseDirectory.load_config_paths("climix"))[::-1]
    for d in directories:
        logging.info(f"Looking for metadata in directory {d}")
    files = sum(
        [find_metadata_files_in_dir(directory) for directory in directories], []
    )
    if metadata_files is not None:
        for f in metadata_files:
            logging.info(f"Adding metadata from file: {f}")
            files.append(f)
    return files


def load_metadata(metadata_files=None, activate_config=None):
    variables = {}
    indices = {}
    climix_config = None
    variable_metadata = []
    index_metadata = []
    climix_config_metadata = []
    for path in find_metadata_files(metadata_files):
        logging.info(f"Reading metadata definitions from file {path}")
        with open(path) as md_file:
            metadata = yaml.safe_load(md_file)
        dist = build_distribution(metadata)
        index_metadata.append((metadata.get("indices", {}), path, dist))
        variable_metadata.append((metadata.get("variables", {}), path, dist))
        climix_config_metadata.append((metadata.get("climix", {}), path))
    for var_metadata, path, dist in variable_metadata:
        for name, var in var_metadata.items():
            if name in variables:
                logging.info(
                    f"Replacing variable definition for <{name}> with "
                    f"definition from distribution <{dist.name}-{dist.version}> "
                    f"({path})."
                )
            variables[name] = build_variable(name, var, path)
    for idx_metadata, path, dist in index_metadata:
        for name, idx_meta in idx_metadata.items():
            if name in indices:
                logging.info(
                    f"Replacing index definition for <{name}> with "
                    f"definition from distribution <{dist.name}-{dist.version}> "
                    f"({path})."
                )
            try:
                indices[name] = build_index(idx_meta, variables, path, dist)
            except (KeyError, TypeError):
                logging.error("Metadata error for index {} from {}.".format(name, path))
                raise
    if activate_config:
        global_attr_config = None
        for config_metadata, path in climix_config_metadata:
            if "global_attributes" in config_metadata:
                global_attr_config = config_metadata.get("global_attributes", {})
                global_attr_path = path
        if global_attr_config:
            logging.info(
                "Building global attributes configuration with definition from file "
                f"{global_attr_path}"
            )
            try:
                climix_config = {
                    "global_attributes": build_global_attr_config(global_attr_config)
                }
            except (KeyError, TypeError):
                logging.error(
                    f"Metadata error for climix configuration {global_attr_config} "
                    f"from {global_attr_path}."
                )
                raise
    return IndexCatalog(indices), climix_config
