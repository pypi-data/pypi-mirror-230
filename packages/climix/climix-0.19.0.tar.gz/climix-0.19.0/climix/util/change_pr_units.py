# -*- coding: utf-8 -*-

from collections import namedtuple, OrderedDict

from cf_units import Unit
import iris


DENSITY_WATER = Unit("1000 kg m-3")


PrecipQty = namedtuple("PrecipQty", ["units", "is_rate_based", "is_mass_based"])


PRECIPITATION_INFO = OrderedDict(
    [
        ("lwe_precipitation_rate", PrecipQty(Unit("m s-1"), True, False)),
        ("lwe_thickness_of_precipitation_amount", PrecipQty(Unit("m"), False, False)),
        ("thickness_of_rainfall_amount", PrecipQty(Unit("m"), False, False)),
        ("precipitation_amount", PrecipQty(Unit("kg m-2"), False, True)),
        ("precipitation_flux", PrecipQty(Unit("kg m-2 s-1"), True, True)),
    ]
)


def is_precipitation(standard_name):
    return standard_name in PRECIPITATION_INFO.keys()


def get_standard_name_for_units(units):
    for standard_name, qty in PRECIPITATION_INFO.items():
        if units.is_convertible(qty.units):
            return standard_name
    raise ValueError(f"change_pr_units: Cannot handle new units {units}.")


def ensure_units_and_standard_name(units, standard_name):
    if isinstance(units, str):
        units = Unit(units)
    if units is None and standard_name is None:
        raise ValueError("No new units or new standard name is given.")
    if standard_name is None:
        standard_name = get_standard_name_for_units(units)
    try:
        units_dict = PRECIPITATION_INFO[standard_name]
    except KeyError:
        raise ValueError(f"Unknown standard_name {standard_name}.")
    if units is None:
        units = units_dict.units
    if not units.is_convertible(units_dict.units):
        raise ValueError(
            f"Cannot handle new units {units}. "
            f"Not fitting standard_name, {standard_name}."
        )
    return units, standard_name


def get_rate_conversion(old_qty, new_qty, integration_time):
    if old_qty.is_rate_based and not new_qty.is_rate_based:
        return integration_time
    if not old_qty.is_rate_based and new_qty.is_rate_based:
        return integration_time.invert()
    return 1.0


def get_mass_conversion(old_qty, new_qty, density):
    if old_qty.is_mass_based and not new_qty.is_mass_based:
        return density.invert()
    if not old_qty.is_mass_based and new_qty.is_mass_based:
        return density
    return 1.0


def change_pr_units(
    cube_or_coord,
    new_units=None,
    new_standard_name=None,
    integration_time=Unit("1 day"),
    density=DENSITY_WATER,
):
    """Converts precipitation units considering standard names.

    Converts precipitation units and data to requested units.
    Standard names are converted too, if required.

    Parameters
    ----------
    cube_or_coord: iris.cube.Cube or iris.coords.Coord
        precipitation data
    new_units: cf_units.Unit
        units to convert to
    new_standard_name: str
        standard name to convert to

    Returns
    -------
    iris.cube.Cube or iris.coords.Coord
       cube or coord with new units and standard name

    """
    new_units, new_standard_name = ensure_units_and_standard_name(
        new_units, new_standard_name
    )

    old_units, old_standard_name = ensure_units_and_standard_name(
        cube_or_coord.units, cube_or_coord.standard_name
    )

    old_qty = PRECIPITATION_INFO[old_standard_name]
    new_qty = PRECIPITATION_INFO[new_standard_name]

    conv = get_rate_conversion(
        old_qty, new_qty, integration_time
    ) * get_mass_conversion(old_qty, new_qty, density)

    conv_factor = (old_units * conv).convert(1.0, new_units)
    if isinstance(cube_or_coord, iris.cube.Cube):
        cube_or_coord.data = cube_or_coord.core_data() * float(conv_factor)
    elif isinstance(cube_or_coord, iris.coords.Coord):
        cube_or_coord.points *= float(conv_factor)
        if cube_or_coord.bounds is not None:
            cube_or_coord.bounds *= float(conv_factor)
    cube_or_coord.units = new_units
    cube_or_coord.standard_name = new_standard_name
