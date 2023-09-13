from unittest.mock import patch

from hestia_earth.models.emepEea2019.utils import get_fuel_values

class_path = 'hestia_earth.models.emepEea2019.utils'
TERMS = [
    'diesel',
    'gasoline'
]


@patch(f"{class_path}._is_term_type_complete", return_value=True)
def test_get_fuel_values_no_inputs_complete(*args):
    cycle = {'@type': 'Cycle', 'inputs': []}
    assert get_fuel_values('co2ToAirFuelCombustion', cycle, '') == [0]

    cycle = {'@type': 'Transformation', 'inputs': []}
    assert get_fuel_values('co2ToAirFuelCombustion', cycle, '') == []


@patch(f"{class_path}._is_term_type_complete", return_value=False)
def test_get_fuel_values_no_inputs_incomplete(*args):
    cycle = {'@type': 'Cycle', 'inputs': []}
    assert get_fuel_values('co2ToAirFuelCombustion', cycle, '') == []

    cycle = {'@type': 'Transformation', 'inputs': []}
    assert get_fuel_values('co2ToAirFuelCombustion', cycle, '') == []


def test_get_fuel_values(*args):
    cycle = {
        '@type': 'Cycle',
        'inputs': [
            {
                'term': {'@id': 'diesel', 'termType': 'fuel'},
                'value': [100]
            },
            {
                'term': {'@id': 'gasoline', 'termType': 'fuel'},
                'value': [50]
            }
        ]
    }
    assert get_fuel_values('co2ToAirFuelCombustion', cycle, 'co2ToAirFuelCombustionEmepEea2019') == [317.0]
