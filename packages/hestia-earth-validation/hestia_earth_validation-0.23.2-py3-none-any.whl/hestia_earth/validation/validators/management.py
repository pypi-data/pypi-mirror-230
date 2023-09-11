from typing import List
from hestia_earth.schema import TermTermType, SiteSiteType
from hestia_earth.utils.model import filter_list_term_type

from hestia_earth.validation.utils import _filter_list_errors


def validate_has_termType(site: dict, term_type: TermTermType, site_type: SiteSiteType):
    blank_nodes = filter_list_term_type(site.get('management', []), term_type)
    return site.get('siteType') != site_type.value or len(blank_nodes) > 0 or {
        'level': 'warning',
        'dataPath': '.management',
        'message': 'should contain at least one management node',
        'params': {
            'termType': term_type.value
        }
    }


def validate_has_termTypes(site: dict, term_types: List[TermTermType], site_type: SiteSiteType):
    return _filter_list_errors([
        validate_has_termType(site, term_type, site_type=site_type) for term_type in term_types
    ])
