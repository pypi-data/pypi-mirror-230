"""
Checks for the atmosphere module
"""

# pylint: disable=import-outside-toplevel
from unittest.mock import patch

import astropy.units as u
import numpy as np
import pytest

import ctapipe.atmosphere as atmo
from ctapipe.utils import get_dataset_path

SIMTEL_PATH = get_dataset_path(
    "gamma_20deg_0deg_run2___cta-prod5-paranal_desert"
    "-2147m-Paranal-dark_cone10-100evts.simtel.zst"
)


def get_simtel_profile_from_eventsource():
    """get a TableAtmosphereDensityProfile from a simtel file"""
    from ctapipe.io import EventSource

    with EventSource(SIMTEL_PATH) as source:
        return source.atmosphere_density_profile


@pytest.fixture(scope="session", name="table_profile")
def fixture_table_profile():
    """a table profile for testing"""
    return get_simtel_profile_from_eventsource()


def get_simtel_fivelayer_profile():
    """
    get a sample 3-layer profile
    """
    from ctapipe.io.simteleventsource import (
        AtmosphereProfileKind,
        read_atmosphere_profile_from_simtel,
    )

    return read_atmosphere_profile_from_simtel(
        SIMTEL_PATH, kind=AtmosphereProfileKind.FIVELAYER
    )


@pytest.mark.parametrize(
    "density_model",
    [
        atmo.ExponentialAtmosphereDensityProfile(),
        get_simtel_profile_from_eventsource(),
        get_simtel_fivelayer_profile(),
    ],
)
def test_models(density_model):
    """check that a set of model classes work"""

    # test we can convert to correct units
    density_model(10 * u.km).to(u.kg / u.m**3)

    # ensure units are properly taken into account
    assert np.isclose(density_model(1 * u.km), density_model(1000 * u.m))

    # check we can also compute the integral
    column_density = density_model.integral(10 * u.km)
    assert column_density.unit.is_equivalent(u.g / u.cm**2)

    assert np.isclose(
        density_model.integral(1 * u.km), density_model.integral(1000 * u.m)
    )

    with patch("matplotlib.pyplot.show"):
        density_model.peek()


def test_exponential_model():
    """check exponential models"""

    density_model = atmo.ExponentialAtmosphereDensityProfile(
        scale_height=10 * u.m, scale_density=0.00125 * u.g / u.cm**3
    )
    assert np.isclose(density_model(1_000_000 * u.km), 0 * u.g / u.cm**3)
    assert np.isclose(density_model(0 * u.km), density_model.scale_density)


def test_table_model_interpolation(table_profile):
    """check that interpolation is reasonable"""

    np.testing.assert_allclose(
        table_profile(table_profile.table["height"].to("km")),
        table_profile.table["density"].to("g cm-3"),
    )

    # check that fine interpolation up to 100 km :
    height_fine = np.linspace(0, 100, 1000) * u.km
    assert np.isfinite(table_profile.integral(height_fine)).all()


def test_against_reference():
    """
    Test five-layer and table methods against a reference analysis from
    SimTelArray.  Data from communication with K. Bernloehr.

    See https://github.com/cta-observatory/ctapipe/pull/2000
    """
    from ctapipe.utils import get_table_dataset

    reference_table = get_table_dataset(
        "atmosphere_profile_comparison_from_simtelarray"
    )

    fit_reference = np.array(
        [
            [0.00 * 100000, -140.508, 1178.05, 994186, 0],
            [9.75 * 100000, -18.4377, 1265.08, 708915, 0],
            [19.00 * 100000, 0.217565, 1349.22, 636143, 0],
            [46.00 * 100000, -0.000201796, 703.745, 721128, 0],
            [106.00 * 100000, 0.000763128, 1, 1.57247e10, 0],
        ]
    )

    profile_5 = atmo.FiveLayerAtmosphereDensityProfile.from_array(fit_reference)

    height = reference_table["Altitude_km"].to("km")

    np.testing.assert_allclose(
        1.0 - profile_5(height) / reference_table["rho_5"], 0, atol=1e-5
    )
    np.testing.assert_allclose(
        1.0 - profile_5.line_of_sight_integral(height) / reference_table["thick_5"],
        0,
        atol=1e-5,
    )
