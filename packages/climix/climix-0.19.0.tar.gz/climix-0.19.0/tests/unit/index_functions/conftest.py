import pytest
from iris.cube import Cube
from iris.coords import AuxCoord
import numpy as np
from cf_units import Unit
from iris.coords import DimCoord


def add_dim_coord(cube, time):
    """Add time dimension coordinates to cube."""
    shape = cube.data.shape
    assert len(shape) == 3
    time_coord = DimCoord(
        time,
        var_name="time",
        standard_name="time",
        units="days since 1949-12-01 00:00:00",
    )
    cube.add_dim_coord(time_coord, 0)


@pytest.fixture
def f_time_cube_tas(request):
    test_cube = Cube(
        data=request.param["data"].astype(np.float32),
        standard_name="air_temperature",
        var_name="tas",
        units=request.param["units"],
    )
    if "time" in request.param:
        add_dim_coord(test_cube, request.param["time"])
    return test_cube


@pytest.fixture
def f_cube_tas(request):
    test_cube = Cube(
        data=request.param["data"].astype(np.float32),
        standard_name="air_temperature",
        var_name="tas",
        units=request.param["units"],
    )
    return test_cube


@pytest.fixture
def f_cube_tasmax(request):
    test_cube = Cube(
        data=request.param["data"].astype(np.float32),
        standard_name="air_temperature",
        var_name="tasmax",
        units=request.param["units"],
    )
    return test_cube


@pytest.fixture
def f_cube_tasmin(request):
    test_cube = Cube(
        data=request.param["data"].astype(np.float32),
        standard_name="air_temperature",
        var_name="tasmin",
        units=request.param["units"],
    )
    return test_cube


@pytest.fixture
def f_cube_pr(request):
    test_cube = Cube(
        data=request.param["data"].astype(np.float32),
        standard_name=request.param["standard_name"],
        var_name="pr",
        units=request.param["units"],
    )
    return test_cube


@pytest.fixture
def f_first_threshold(request):
    long_name = "first_threshold"
    if "long_name" in request.param:
        long_name = request.param["long_name"]
    aux_coord = AuxCoord(
        np.array([request.param["data"]]),
        standard_name=request.param["standard_name"],
        units=Unit(request.param["units"]),
        var_name="first_threshold",
        long_name=long_name,
    )
    return aux_coord


@pytest.fixture
def f_second_threshold(request):
    long_name = "second_threshold"
    if "long_name" in request.param:
        long_name = request.param["long_name"]
    aux_coord = AuxCoord(
        np.array([request.param["data"]]),
        standard_name=request.param["standard_name"],
        units=Unit(request.param["units"]),
        var_name="second_threshold",
        long_name=long_name,
    )
    return aux_coord


@pytest.fixture
def f_percentile(request):
    aux_coord = AuxCoord(
        np.array([request.param["data"]]),
        units=Unit(request.param["units"]),
    )
    return aux_coord


@pytest.fixture
def f_window_size(request):
    aux_coord = AuxCoord(
        np.array([request.param["data"]]),
        units=Unit(request.param["units"]),
    )
    return aux_coord
