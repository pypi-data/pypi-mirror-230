import os
from hestia_earth.schema import NodeType

from .log import logger

ENABLED = os.getenv('VALIDATE_SPATIAL', 'true') == 'true'
ENABLE_TYPES = [NodeType.SITE.value, NodeType.ORGANISATION.value]
MAX_AREA_SIZE = int(os.getenv('MAX_AREA_SIZE', '5000'))
CACHING_ENABLED = os.getenv('SPATIAL_CACHING_ENABLED', 'true') == 'true'

_caching = {}


def init_gee_by_nodes(nodes: list):
    # need to validate for non-aggregated Site or Oganisation
    should_init = any([
        n.get('@type', n.get('type')) in ENABLE_TYPES for n in nodes if not n.get('aggregated', False)
    ])
    if should_init and ENABLED:
        try:
            from hestia_earth.earth_engine import init_gee
        except ImportError:
            logger.error("Run `pip install hestia_earth.earth_engine` to use geospatial validation")
        return init_gee()
    return None


def is_enabled():
    if ENABLED:
        try:
            from hestia_earth.earth_engine.version import VERSION
            logger.debug("Using earth_engine version %s", VERSION)
            return True
        except ImportError:
            logger.error("Run `pip install hestia_earth.earth_engine` to use geospatial validation")

    return False


def id_to_level(id: str): return id.count('.')


def _caching_key(func_name: str, args: dict):
    return '-'.join([func_name, str(args)])


def _run_with_cache(func_name: str, args: dict, func):
    global _caching
    key = _caching_key(func_name, args)
    if CACHING_ENABLED:
        _caching[key] = _caching.get(key) if key in _caching else func()
        return _caching[key]
    else:
        return func()


def fetch_data_by_coordinates(**kwargs):
    from hestia_earth.earth_engine.coordinates import run
    return _run_with_cache('fetch_data_by_coordinates',
                           kwargs,
                           lambda *args: run(kwargs).get('features', [])[0].get('properties'))


def get_region_id(gid: str, **kwargs):
    try:
        level = id_to_level(gid)
        field = f"GID_{level}"
        id = fetch_data_by_coordinates(
            collection=f"users/hestiaplatform/gadm36_{level}",
            ee_type='vector',
            fields=field,
            **kwargs
        ).get(field)
        return None if id is None else f"GADM-{id}"
    except Exception:
        return None


def get_region_distance(gid: str, latitude: float, longitude: float):
    global _caching
    try:
        from hestia_earth.earth_engine.gadm import get_distance_to_coordinates
        return _run_with_cache('get_region_distance',
                               {'gid': gid, 'latitude': latitude, 'longitude': longitude},
                               round(get_distance_to_coordinates(gid, latitude=latitude, longitude=longitude) / 1000))
    except Exception:
        return None
