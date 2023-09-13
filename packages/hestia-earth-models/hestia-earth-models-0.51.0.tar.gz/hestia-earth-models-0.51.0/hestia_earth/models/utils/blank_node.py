from hestia_earth.utils.api import download_hestia
from hestia_earth.utils.tools import list_sum, safe_parse_float, non_empty_list

from ..log import debugValues
from . import _filter_list_term_unit
from .constant import Units
from .property import get_node_property
from .lookup import (
    is_model_siteType_allowed,
    is_siteType_allowed, is_product_id_allowed, is_product_termType_allowed
)


def group_by_keys(group_keys: list = ['term']):
    def run(group: dict, input: dict):
        group_key = '-'.join(non_empty_list(map(lambda v: input.get(v, {}).get('@id'), group_keys)))
        group[group_key] = group.get(group_key, []) + [input]
        return group
    return run


def _module_term_id(term_id: str, module): return getattr(module, 'TERM_ID', term_id).split(',')[0]


def _run_model_required(model: str, term: dict, data: dict):
    siteType_allowed = is_model_siteType_allowed(model, term, data)

    run_required = all([siteType_allowed])
    debugValues(data, model=model, term=term.get('@id'),
                run_required=run_required,
                siteType_allowed=siteType_allowed)
    return run_required


def _run_required(model: str, term: dict, data: dict):
    siteType_allowed = is_siteType_allowed(data, term)
    product_id_allowed = is_product_id_allowed(data, term)
    product_termType_allowed = is_product_termType_allowed(data, term)

    run_required = all([siteType_allowed, product_id_allowed, product_termType_allowed])
    # model is only used for logs here, skip logs if model not provided
    if model:
        debugValues(data, model=model, term=term.get('@id'),
                    siteType_allowed=siteType_allowed,
                    product_id_allowed=product_id_allowed,
                    product_termType_allowed=product_termType_allowed)
        # logging this for the model would cause issues parsing statuses
        if model != 'emissionNotRelevant':
            debugValues(data, model=model, term=term.get('@id'), run_required=run_required)
    return run_required


def is_run_required(model: str, term_id: str, node: dict):
    """
    Determines whether the term for the model should run or not, based on lookup values.

    Parameters
    ----------
    model : str
        The `@id` of the model. Example: `pooreNemecek2018`.
    term_id : str
        The `@id` of the `Term` or the full JSON-LD of the Term. Example: `sandContent`.
    node : dict
        The node on which the model is applied. Logging purpose ony.

    Returns
    -------
    bool
        True if the model is required to run.
    """
    term = download_hestia(term_id)
    return (
        (_run_model_required(model, term, node) if model else True) and _run_required(model, term, node)
    ) if term else True


def run_if_required(model: str, term_id: str, data: dict, module):
    return getattr(module, 'run')(data) if is_run_required(model, _module_term_id(term_id, module), data) else []


def find_terms_value(nodes: list, term_id: str):
    """
    Returns the sum of all blank nodes in the list which match the `Term` with the given `@id`.

    Parameters
    ----------
    values : list
        The list in which to search for. Example: `cycle['nodes']`.
    term_id : str
        The `@id` of the `Term`. Example: `sandContent`

    Returns
    -------
    float
        The total `value` as a number.
    """
    return list_sum(get_total_value(filter(lambda node: node.get('term', {}).get('@id') == term_id, nodes)))


def get_total_value(nodes: list):
    """
    Get the total `value` of a list of Blank Nodes.
    This method does not take into account the `units` and possible conversions.

    Parameters
    ----------
    nodes : list
        A list of Blank Node.

    Returns
    -------
    list
        The total `value` as a list of numbers.
    """
    return list(map(lambda node: list_sum(node.get('value', [])), nodes))


def _value_as(term_id: str, convert_to_property=True):
    def get_value(node: dict):
        property = get_node_property(node, term_id)
        # ignore node value if property is not found
        factor = safe_parse_float(property.get('value', 0))
        value = list_sum(node.get('value', []))
        ratio = factor / 100 if property.get('term', {}).get('units', '') == '%' else factor
        return 0 if ratio == 0 else (value * ratio if convert_to_property else value / ratio)
    return get_value


def get_total_value_converted(nodes: list, conversion_property, convert_to_property=True):
    """
    Get the total `value` of a list of Blank Nodes converted using a property of each Blank Node.

    Parameters
    ----------
    nodes : list
        A list of Blank Node.
    conversion_property : str|List[str]
        Property (or multiple properties) used for the conversion. Example: `nitrogenContent`.
        See https://hestia.earth/glossary?termType=property for a list of `Property`.
    convert_to_property : bool
        By default, property is multiplied on value to get result. Set `False` to divide instead.

    Returns
    -------
    list
        The total `value` as a list of numbers.
    """
    def convert_multiple(node: dict):
        value = 0
        for prop in conversion_property:
            value = _value_as(prop, convert_to_property)(node)
            node['value'] = [value]
        return value

    return [
        _value_as(conversion_property, convert_to_property)(node) if isinstance(conversion_property, str) else
        convert_multiple(node) for node in nodes
    ]


def get_N_total(nodes: list) -> list:
    """
    Get the total nitrogen content of a list of Blank Node.

    The result contains the values of the following nodes:
    1. Every blank node in `kg N` will be used.
    2. Every blank node specified in `kg` will be multiplied by the `nitrogenContent` property.

    Parameters
    ----------
    nodes : list
        A list of Blank Node.

    Returns
    -------
    list
        The nitrogen values as a list of numbers.
    """
    kg_N_nodes = _filter_list_term_unit(nodes, Units.KG_N)
    kg_nodes = _filter_list_term_unit(nodes, Units.KG)
    return get_total_value(kg_N_nodes) + get_total_value_converted(kg_nodes, 'nitrogenContent')


def get_KG_total(nodes: list) -> list:
    """
    Get the total kg mass of a list of Blank Node.

    The result contains the values of the following nodes:
    1. Every blank node in `kg` will be used.
    2. Every blank node specified in `kg N` will be divided by the `nitrogenContent` property.

    Parameters
    ----------
    nodes : list
        A list of Blank Node.

    Returns
    -------
    list
        The nitrogen values as a list of numbers.
    """
    kg_N_nodes = _filter_list_term_unit(nodes, Units.KG_N)
    kg_nodes = _filter_list_term_unit(nodes, Units.KG)
    return get_total_value(kg_nodes) + get_total_value_converted(kg_N_nodes, 'nitrogenContent', False)


def get_P2O5_total(nodes: list) -> list:
    """
    Get the total phosphate content of a list of Blank Node.

    The result contains the values of the following nodes:
    1. Every organic fertiliser specified in `kg P2O5` will be used.
    1. Every organic fertiliser specified in `kg N` will be multiplied by the `phosphateContentAsP2O5` property.
    2. Every organic fertiliser specified in `kg` will be multiplied by the `phosphateContentAsP2O5` property.

    Parameters
    ----------
    nodes : list
        A list of Blank Node.

    Returns
    -------
    list
        The phosphate values as a list of numbers.
    """
    kg_P_nodes = _filter_list_term_unit(nodes, Units.KG_P2O5)
    kg_N_nodes = _filter_list_term_unit(nodes, Units.KG_N)
    kg_nodes = _filter_list_term_unit(nodes, Units.KG)
    return get_total_value(kg_P_nodes) + get_total_value_converted(kg_N_nodes + kg_nodes, 'phosphateContentAsP2O5')
