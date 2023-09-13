from hestia_earth.schema import MeasurementStatsDefinition, MeasurementMethodClassification, SiteSiteType

from hestia_earth.models.log import logShouldRun
from hestia_earth.models.utils.measurement import _new_measurement
from . import MODEL

REQUIREMENTS = {
    "Site": {}
}
RETURNS = {
    "Measurement": [{
        "value": "",
        "statsDefinition": "modelled",
        "methodClassification": "modelled using other physical measurements"
    }]
}
LOOKUPS = {
    "crop": "Non_bearing_duration"
}
TERM_ID = 'waterDepth'
BIBLIO_TITLE = 'Reducing food’s environmental impacts through producers and consumers'
SITE_TYPE_TO_DEPTH = {
    SiteSiteType.POND.value: 1.5,
    SiteSiteType.RIVER_OR_STREAM.value: 1,
    SiteSiteType.LAKE.value: 20,
    SiteSiteType.SEA_OR_OCEAN.value: 40
}


def measurement(value: float):
    data = _new_measurement(TERM_ID, None, BIBLIO_TITLE)
    data['value'] = [value]
    data['statsDefinition'] = MeasurementStatsDefinition.MODELLED.value
    data['methodClassification'] = MeasurementMethodClassification.MODELLED_USING_OTHER_PHYSICAL_MEASUREMENTS.value
    return data


def _run(site: dict):
    logShouldRun(site, MODEL, TERM_ID, True)
    site_type = site.get('siteType')
    value = SITE_TYPE_TO_DEPTH.get(site_type, 0)
    return measurement(value) if value else None


def run(site: dict): return _run(site)
