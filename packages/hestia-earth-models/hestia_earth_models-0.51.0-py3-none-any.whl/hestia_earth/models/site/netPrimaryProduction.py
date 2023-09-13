from hestia_earth.schema import MeasurementStatsDefinition, MeasurementMethodClassification
from hestia_earth.utils.model import find_term_match

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.measurement import _new_measurement, measurement_value
from hestia_earth.models.utils.temperature import TemperatureLevel, get_level
from . import MODEL

REQUIREMENTS = {
    "Site": {
        "measurements": [{"@type": "Measurement", "value": "", "term.@id": "temperatureAnnual"}]
    }
}
RETURNS = {
    "Measurement": [{
        "value": "",
        "statsDefinition": "modelled",
        "methodClassification": "modelled using other physical measurements"
    }]
}
TERM_ID = 'netPrimaryProduction'
BIBLIO_TITLE = 'Reducing food’s environmental impacts through producers and consumers'
NPP_Aqua = {TemperatureLevel.LOW: 2, TemperatureLevel.MEDIUM: 4, TemperatureLevel.HIGH: 5}


def _measurement(value: float):
    data = _new_measurement(TERM_ID, None, BIBLIO_TITLE)
    data['value'] = [value]
    data['statsDefinition'] = MeasurementStatsDefinition.MODELLED.value
    data['methodClassification'] = MeasurementMethodClassification.MODELLED_USING_OTHER_PHYSICAL_MEASUREMENTS.value
    return data


def _npp(temp: float): return NPP_Aqua.get(get_level(temperature=temp), 0)


def _run(temp: float):
    value = _npp(temp)
    return [_measurement(value)]


def _should_run(site: dict):
    measurements = site.get('measurements', [])
    temperature = measurement_value(find_term_match(measurements, 'temperatureAnnual'))

    logRequirements(site, model=MODEL, term=TERM_ID,
                    temperature=temperature)

    should_run = temperature > 0
    logShouldRun(site, MODEL, TERM_ID, should_run)
    return should_run, temperature


def run(site: dict):
    should_run, temp = _should_run(site)
    return _run(temp) if should_run else []
