from hestia_earth.schema import TermTermType

from hestia_earth.models.geospatialDatabase.utils import get_region_factor


def test_get_region_factor():
    site = {'country': {'@id': 'GADM-ALB'}}
    assert get_region_factor('croppingIntensity', site, TermTermType.LANDUSEMANAGEMENT) == 0.9999775685587958
