from pollination.irradiance.entry import SkyIrradianceEntryPoint
from queenbee.recipe.dag import DAG


def test_annual_sky_radiation():
    recipe = SkyIrradianceEntryPoint().queenbee
    assert recipe.name == 'sky-irradiance-entry-point'
    assert isinstance(recipe, DAG)
