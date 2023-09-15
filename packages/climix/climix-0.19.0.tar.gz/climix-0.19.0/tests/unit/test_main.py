import pytest
from climix import main


TEST_FILE_LIST_TO_GUESS_OUTPUT_TEMPLATE = [
    (
        ["tas_foo_historical_bar_day_19700101.nc"],
        "{var_name}_foo_historical_bar_{frequency}_19700101-19700101.nc",
    ),
    (
        ["tas_foo_historical_bar_day_19700101-19801231.nc"],
        "{var_name}_foo_historical_bar_{frequency}_19700101-19801231.nc",
    ),
    (
        [
            "tas_foo_historical_bar_day_19700101-19801231.nc",
            "tas_foo_historical_bar_day_19800101-19901231.nc",
        ],
        "{var_name}_foo_historical_bar_{frequency}_19700101-19901231.nc",
    ),
    (
        [
            "tas_foo_historical_bar_day_19900101-20001231.nc",
            "tas_foo_rcp26_bar_day_20010101-20101231.nc",
        ],
        "{var_name}_foo_historical-rcp26_bar_{frequency}_19900101-20101231.nc",
    ),
    (
        [
            "tas_foo_historical_bar_day_19900101-20001231.nc",
            "tas_foo_rcp85_bar_day_20010101-20101231.nc",
        ],
        "{var_name}_foo_historical-rcp85_bar_{frequency}_19900101-20101231.nc",
    ),
    (
        [
            "tas_foo_historical_bar_day_19900101-20001231.nc",
            "tas_foo_ssp119_bar_day_20010101-20101231.nc",
        ],
        "{var_name}_foo_historical-ssp119_bar_{frequency}_19900101-20101231.nc",
    ),
    (
        [
            "tas_foo_historical_bar_day_19900101-20001231.nc",
            "tas_foo_ssp585_bar_day_20010101-20101231.nc",
        ],
        "{var_name}_foo_historical-ssp585_bar_{frequency}_19900101-20101231.nc",
    ),
    (["tas_foo_historical_bar_day.nc"], "{var_name}_foo_historical_bar_{frequency}.nc"),
    (
        ["tas_foo_historical_bar_day_notimerange.nc"],
        "{var_name}_foo_historical_bar_{frequency}.nc",
    ),
    (
        ["tas_foo_historical_bar_notimerange.nc", "tas_foo_rcp45_bar_notimerange.nc"],
        "{var_name}_foo_historical-rcp45_bar_{frequency}.nc",
    ),
    (["foobar.nc"], "{var_name}_{frequency}.nc"),
]


@pytest.mark.parametrize(
    "file_list, expected_output_template", TEST_FILE_LIST_TO_GUESS_OUTPUT_TEMPLATE
)
def test_guess_output_template(file_list, expected_output_template):
    """Test ``guess_output_template``."""
    output_template = main.guess_output_template(file_list)
    assert output_template == expected_output_template
