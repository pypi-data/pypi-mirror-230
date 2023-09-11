import pytest

from mwtp._namespace_id_map import NamespaceIDMap


@pytest.fixture(scope = 'module')
def keys():
	yield ['FoO', 'bAr']


@pytest.fixture(scope = 'module')
def namespace_id_map():
	map_instance = NamespaceIDMap()
	
	yield map_instance


def test_repr(namespace_id_map):
	assert isinstance(repr(namespace_id_map), str)


def test_setitem(namespace_id_map, keys):
	for key in keys:
		namespace_id_map[key] = 42


def test_setitem_non_string_key(namespace_id_map):
	with pytest.raises(TypeError):
		namespace_id_map[42] = 42


def test_setitem_non_integer_value(namespace_id_map):
	with pytest.raises(TypeError):
		namespace_id_map['lorem'] = 'ipsum'


def test_getitem(namespace_id_map):
	assert namespace_id_map['fOo'] == 42


def test_contains_true(namespace_id_map):
	assert 'fOO' in namespace_id_map


def test_contains_false(namespace_id_map):
	assert 'BAz' not in namespace_id_map


def test_len(namespace_id_map, keys):
	assert len(namespace_id_map) == len(keys)


def test_delitem(namespace_id_map):
	with pytest.raises(TypeError):
		del namespace_id_map['foo']


def test_iter(namespace_id_map, keys):
	assert [*namespace_id_map] == [key.lower() for key in keys]
