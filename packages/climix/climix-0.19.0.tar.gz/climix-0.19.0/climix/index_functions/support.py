# -*- coding: utf-8 -*-
import logging
from collections import namedtuple
from datetime import (
    datetime,
    time,
)
import isodate
import operator
import re

from cf_units import Unit
import cftime
import dask.array as da
import iris
import numpy as np

from ..util import change_units


SUPPORTED_OPERATORS = [
    "<",
    ">",
    "<=",
    ">=",
]
SUPPORTED_REDUCERS = [
    "min",
    "max",
    "sum",
    "mean",
]


def scalar_mean(*args):
    return float(np.mean(args))


SCALAR_OPERATORS = {
    "<": operator.lt,
    ">": operator.gt,
    "<=": operator.le,
    ">=": operator.ge,
}
SCALAR_REDUCERS = {
    "min": min,
    "max": max,
    "sum": sum,
    "mean": scalar_mean,
}


NUMPY_OPERATORS = {
    "<": np.less,
    ">": np.greater,
    "<=": np.less_equal,
    ">=": np.greater_equal,
}
NUMPY_REDUCERS = {
    "min": np.min,
    "max": np.max,
    "sum": np.sum,
    "mean": np.mean,
}


DASK_OPERATORS = {
    "<": da.less,
    ">": da.greater,
    "<=": da.less_equal,
    ">=": da.greater_equal,
}
DASK_REDUCERS = {
    "min": da.min,
    "max": da.max,
    "sum": da.sum,
    "mean": da.mean,
}


TimeRange = namedtuple("TimeRange", ["start", "end", "climatological"])


TIME_FORMATS = {
    4: "%Y",
    6: "%Y%m",
    8: "%Y%m%d",
    10: "%Y%m%d%H",
    12: "%Y%m%d%H%M",
    14: "%Y%m%d%H%M%S",
}


def parse_timerange(timerange):
    parts = timerange.split("-")
    n = len(parts)
    if n < 2 or n > 3:
        raise ValueError(f"Invalid timerange {timerange}")
    if n == 3:
        if parts[2] != "clim":
            raise ValueError(f"Invalid timerange {timerange}")
        climatological = True
    else:
        climatological = False
    n_start = len(parts[0])
    n_end = len(parts[1])
    if n_start != n_end:
        raise ValueError(
            f"Start and end time must have the same resolution in {timerange}"
        )
    format_string = TIME_FORMATS[n_start]
    start_time = datetime.strptime(parts[0], format_string)
    end_time = datetime.strptime(parts[1], format_string)
    return TimeRange(start_time, end_time, climatological)


def parse_isodate(date):
    """
    Parses a date string in ISO 8601 format and
    return a datetime object.
    """
    parsed_date = isodate.parse_date(date)
    return datetime.combine(parsed_date, time.min)


def parse_isodate_upper_bound(date):
    """
    Parses a four-digit year or calendar date string in ISO8601 format
    and returns the upper bound for the time interval defined by the
    precision of the given date (i.e. the strings `1990`, `1990-12` and
    `1990-12-31` will all result in a datetime object with the time
    `1991-01-01T00:00:00`).
    """
    parsed_date = isodate.parse_date(date)
    if re.fullmatch(r"[0-9]{4}", date):  # YYYY
        parsed_date = parsed_date + isodate.Duration(years=1)
    elif re.fullmatch(r"[0-9]{4}-[0-9]{2}", date):  # YYYY-MM
        parsed_date = parsed_date + isodate.Duration(months=1)
    elif re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", date):  # YYYY-MM-DD
        parsed_date = parsed_date + isodate.Duration(days=1)
    else:
        raise ValueError(
            "Only four-digit years and calendar dates in ISO8601 format are supported."
        )
    return datetime.combine(parsed_date, time.min)


def parse_isodate_timerange(timerange):
    """
    Parses a time interval in ISO8601 format.
    """
    try:
        start, end = timerange.split("/")
    except ValueError as e:
        raise ValueError(
            "timerange string must contain one and only one slash ('/')"
        ) from e
    if start.startswith("P"):
        end_date = parse_isodate_upper_bound(end)
        start_date = end_date - isodate.parse_duration(start)
    elif end.startswith("P"):
        start_date = parse_isodate(start)
        end_date = start_date + isodate.parse_duration(end)
    else:
        start_date = parse_isodate(start)
        end_date = parse_isodate_upper_bound(end)
    if start_date >= end_date:
        raise ValueError("Start date must be earlier than end date.")
    return TimeRange(start_date, end_date, False)


class TimesHelper:
    def __init__(self, time):
        self.times = time.core_points()
        self.units = str(time.units)

    def __getattr__(self, name):
        return getattr(self.times, name)

    def __len__(self):
        return len(self.times)

    def __getitem__(self, key):
        return self.times[key]


class ReferencePeriod:
    """
    Builds the reference period from the time coordinate and the timerange. Stores
    information about first and last year, start and end index for the cube data,
    and a auxiliary coordinate with information.
    """

    def __init__(self, cube, reference_period):
        self.timerange = parse_isodate_timerange(reference_period)
        self.first_year = self.timerange.start.year
        self.last_year = self.timerange.end.year - 1
        logging.info(f"Building reference period <{reference_period}>")
        time = cube.coord("time")
        indices, bounds = self._get_indices_and_bnds(time, self.timerange)
        self.idx_0, self.idx_n = indices
        bnds_start, bnds_end = bounds
        middle_point = (bnds_start + bnds_end) / 2
        bounds = np.array([bnds_start, bnds_end])
        self.aux_coord = iris.coords.AuxCoord(
            var_name="reference_period",
            standard_name="reference_epoch",
            points=middle_point,
            bounds=bounds,
            units=time.units,
        )

    def _compare_data_period_bnds(self, time, bnds_start, bnds_end):
        """
        Check that the boundaries does not exceed the time range.
        """
        if bnds_start < time.bounds[0][0] or (bnds_end - 1) > time.bounds[-1][1]:
            start_date = cftime.num2date(
                time.bounds[0][0], time.units.name, calendar=time.units.calendar
            )
            end_date = cftime.num2date(
                time.bounds[-1][1], time.units.name, calendar=time.units.calendar
            )
            raise ValueError(
                "The reference period cannot be outside of the data time range. "
                f"Choose a reference period between <{start_date}, {end_date}>"
            )

    def _get_indices_and_bnds(self, time, timerange):
        """
        Returns the start and end index and the boundary points in relation to the cube
        time coordinate
        """
        time_units = time.units
        times = TimesHelper(time)
        bnds_start = cftime.date2num(
            timerange.start, time_units.name, calendar=time_units.calendar
        )
        bnds_end = cftime.date2num(
            timerange.end, time_units.name, calendar=time_units.calendar
        )
        self._compare_data_period_bnds(time, bnds_start, bnds_end)
        idx_0 = cftime.date2index(
            timerange.start, times, calendar=time_units.calendar, select="after"
        )
        idx_n = cftime.date2index(
            timerange.end, times, calendar=time_units.calendar, select="before"
        )
        if time[idx_n].points[0] == bnds_end:
            # If the end date exists exactly in the data, don't include it.
            # E.g., reference period "2014/2018" should have bounds
            # [2014-01-01T00:00:00, 2019-01-01T00:00:00] and the indexing of the data
            # should be the first time step after 2014-01-01T00:00:00 and the last time
            # step before 2019-01-01T00:00:00.
            idx_n -= 1
        return (idx_0, idx_n), (bnds_start, bnds_end)


def normalize_axis(axis, ndim):
    if isinstance(axis, list) and len(axis) == 1:
        axis = axis[0]
    if axis < 0:
        # just cope with negative axis numbers
        axis += ndim
    return axis


class IndexFunction:
    def __init__(self, standard_name=None, units=Unit("no_unit")):
        super().__init__()
        self.standard_name = standard_name
        self.units = units
        self.extra_coords = []

    def preprocess(self, cubes, client):
        pass

    def prepare(self, input_cubes):
        pass

    def pre_aggregate_shape(self, *args, **kwargs):
        return ()


class ThresholdMixin:
    def __init__(self, threshold, condition, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.threshold = threshold
        self.condition = NUMPY_OPERATORS[condition]
        self.lazy_condition = DASK_OPERATORS[condition]
        self.extra_coords.append(threshold.copy())

    def prepare(self, input_cubes):
        ref_cube = next(iter(input_cubes.values()))
        threshold = self.threshold
        threshold.points = threshold.points.astype(ref_cube.dtype)
        if threshold.has_bounds():
            threshold.bounds = threshold.bounds.astype(ref_cube.dtype)
        change_units(threshold, ref_cube.units, ref_cube.standard_name)
        super().prepare(input_cubes)


class ReducerMixin:
    def __init__(self, reducer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reducer = NUMPY_REDUCERS[reducer]
        self.lazy_reducer = DASK_REDUCERS[reducer]
        self.scalar_reducer = SCALAR_REDUCERS[reducer]


class RollingWindowMixin:
    def __init__(self, rolling_aggregator, window_size, reducer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reducer = NUMPY_REDUCERS[reducer]
        self.lazy_reducer = DASK_REDUCERS[reducer]
        self.window_size = window_size
        self.rolling_aggregator = NUMPY_REDUCERS[rolling_aggregator]
        self.lazy_rolling_aggregator = DASK_REDUCERS[rolling_aggregator]
