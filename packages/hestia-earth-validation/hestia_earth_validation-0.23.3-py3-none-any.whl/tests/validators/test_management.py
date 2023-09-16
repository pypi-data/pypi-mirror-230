import os
import json
from hestia_earth.schema import TermTermType, SiteSiteType

from tests.utils import fixtures_path
from hestia_earth.validation.validators.management import (
    validate_has_termType,
    validate_has_termTypes
)

fixtures_folder = os.path.join(fixtures_path, 'management')


def test_validate_has_termType_valid():
    with open(f"{fixtures_folder}/termType/valid-cropland.json") as f:
        site = json.load(f)

    assert validate_has_termType(site, TermTermType.LANDUSEMANAGEMENT, SiteSiteType.CROPLAND) is True

    with open(f"{fixtures_folder}/termType/valid-permanent-pasture.json") as f:
        site = json.load(f)

    assert validate_has_termType(site, TermTermType.LANDUSEMANAGEMENT, SiteSiteType.PERMANENT_PASTURE) is True


def test_validate_has_termType_invalid():
    with open(f"{fixtures_folder}/termType/invalid-cropland.json") as f:
        site = json.load(f)

    assert validate_has_termType(site, TermTermType.LANDUSEMANAGEMENT, SiteSiteType.CROPLAND) == {
        'level': 'warning',
        'dataPath': '.management',
        'message': 'should contain at least one management node',
        'params': {
            'termType': 'landUseManagement'
        }
    }

    with open(f"{fixtures_folder}/termType/invalid-permanent-pasture.json") as f:
        site = json.load(f)

    assert validate_has_termType(site, TermTermType.WATERREGIME, SiteSiteType.PERMANENT_PASTURE) == {
        'level': 'warning',
        'dataPath': '.management',
        'message': 'should contain at least one management node',
        'params': {
            'termType': 'waterRegime'
        }
    }


def test_validate_has_termTypes_valid():
    with open(f"{fixtures_folder}/termType/valid-cropland.json") as f:
        site = json.load(f)

    assert validate_has_termTypes(site, [
        TermTermType.LANDUSEMANAGEMENT,
        TermTermType.WATERREGIME
    ], SiteSiteType.CROPLAND) is True

    with open(f"{fixtures_folder}/termType/valid-permanent-pasture.json") as f:
        site = json.load(f)

    assert validate_has_termTypes(site, [
        TermTermType.LANDUSEMANAGEMENT,
        TermTermType.WATERREGIME
    ], SiteSiteType.PERMANENT_PASTURE) is True


def test_validate_has_termTypes_invalid():
    with open(f"{fixtures_folder}/termType/invalid-cropland.json") as f:
        site = json.load(f)

    assert validate_has_termTypes(site, [
        TermTermType.LANDUSEMANAGEMENT,
        TermTermType.WATERREGIME
    ], SiteSiteType.CROPLAND) == [
        {
            'level': 'warning',
            'dataPath': '.management',
            'message': 'should contain at least one management node',
            'params': {
                'termType': 'landUseManagement'
            }
        },
        {
            'level': 'warning',
            'dataPath': '.management',
            'message': 'should contain at least one management node',
            'params': {
                'termType': 'waterRegime'
            }
        }
    ]

    with open(f"{fixtures_folder}/termType/invalid-permanent-pasture.json") as f:
        site = json.load(f)

    assert validate_has_termTypes(site, [
        TermTermType.LANDUSEMANAGEMENT,
        TermTermType.WATERREGIME
    ], SiteSiteType.PERMANENT_PASTURE) == [
        {
            'level': 'warning',
            'dataPath': '.management',
            'message': 'should contain at least one management node',
            'params': {
                'termType': 'landUseManagement'
            }
        },
        {
            'level': 'warning',
            'dataPath': '.management',
            'message': 'should contain at least one management node',
            'params': {
                'termType': 'waterRegime'
            }
        }
    ]
