import pytest
from ddc_utility.metadata import DanubeDataCubeMetadata


@pytest.fixture
def meta():
    return DanubeDataCubeMetadata()


def test_dataset_names(meta):
    assert set(meta.dataset_names) == {
        'METEOROLOGICAL_FORECAST', 'METEOROLOGICAL', 'SOIL', 'NHRL', 'ECOSYSTEM'}


@pytest.mark.parametrize("dataset_name, expected", [
    ('FORECAST', dict),
    ('HISTORICAL', dict),
    ('DAILY', dict),
    ('SOIL1', dict),
    ('NHRL', dict),
    ('ECOSYSTEM', dict),
    ('not_valid', type(None)),
])
def test_dataset_type(meta, dataset_name, expected):
    assert type(meta.dataset(dataset_name)) == expected


def test_dataset_typeerror(meta):
    with pytest.raises(TypeError):
        meta.dataset()


@pytest.mark.parametrize("dataset_name, expected", [
    ('FORECAST', 'WGS84 (EPSG:4326)'),
    ('HISTORICAL', 'WGS84 (EPSG:4326)'),
    ('DAILY', 'WGS84 (EPSG:4326)'),
    ('SOIL1', 'WGS84 (EPSG:4326)'),
    ('NHRL', 'WGS84 (EPSG:4326)'),
    ('ECOSYSTEM', 'WGS84 (EPSG:4326)'),
])
def test_dataset_crs(meta, dataset_name, expected):
    assert meta.dataset('NHRL').get('delivered_product_crs') == expected


@pytest.mark.parametrize("dataset_name, expected", [
    ('FORECAST', 'meteorological'),
    ('HISTORICAL', 'meteorological'),
    ('DAILY', 'meteorological'),
    ('SOIL1', 'soil'),
    ('NHRL', 'environmental'),
    ('ECOSYSTEM', 'environmental'),
])
def test_dataset_collection_name(meta, dataset_name, expected):
    assert meta.dataset_collection_name(dataset_name) == expected


def test_dataset_vars(meta):
    assert set(meta.dataset_vars('FORECAST').keys()) == {
        'precipitation', 'temperature_max', 'temperature_min'}
    with pytest.raises(AttributeError):
        meta.dataset_vars('not_valid').keys()


def test_dataset_vars_names(meta):
    assert set(meta.dataset_vars_names('FORECAST')) == {
        'precipitation', 'temperature_max', 'temperature_min'}


def test_dataset_var(meta):
    assert meta.dataset_var('NHRL', 'nhrl').get(
        'standard_name') == 'landcover_categories'
    with pytest.raises(AttributeError):
        meta.dataset_var('NHRL', 'not_valid').get('standard_name')


@pytest.mark.parametrize("collection_name, expected", [
    ('meteorological', {'DAILY', 'FORECAST', 'HISTORICAL'}),
    ('soil', {'SOIL1'}),
    ('environmental', {'ECOSYSTEM', 'NHRL'}),
])
def test_dataset_by_collection_name(meta, collection_name, expected):
    assert set(meta.dataset_by_collection_name(
        collection_name).keys()) == expected
