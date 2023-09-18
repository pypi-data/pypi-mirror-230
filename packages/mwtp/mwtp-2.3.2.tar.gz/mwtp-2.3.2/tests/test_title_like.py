import pytest

from mwtp._title_like import TitleLike


def test_contains():
	title_like = TitleLike('Foo')
	
	assert 'oo' in title_like


def test_eq_title_like():
	title_like_1 = TitleLike('Foo')
	title_like_2 = TitleLike('Foo')
	
	assert title_like_1 == title_like_2


def test_eq_str():
	title_like = TitleLike('Foobar')
	
	assert title_like == 'Foobar'


def test_eq_not_implemented():
	title_like = TitleLike('Foobar')
	
	assert (title_like == {}) is False


def test_getitem_int():
	title_like = TitleLike('Foobar')
	
	assert title_like[1] == 'o'


def test_getitem_slice():
	title_like = TitleLike('Foobar')
	
	assert title_like[1:5] == 'ooba'


def test_len():
	title_like = TitleLike('首页')
	
	assert len(title_like) == 6


def test_ne_title_like():
	title_like_1 = TitleLike('Foo')
	title_like_2 = TitleLike('Bar')
	
	assert title_like_1 != title_like_2


def test_ne_str():
	title_like = TitleLike('Foo')
	
	assert title_like != 'Bar'


def test_ne_not_implemented():
	title_like = TitleLike('Foobar')
	
	assert (title_like != {}) is True


def test_repr():
	title_like = TitleLike('Foobar')
	
	assert repr(title_like) == f"TitleLike('Foobar')"


def test_str():
	title_like = TitleLike('Foobar')
	
	assert str(title_like) == 'Foobar'


def test_set():
	title_like = TitleLike('Foobar')
	title_like.set('Bazqux')
	
	assert title_like == 'Bazqux'


def test_starts_with():
	title_like = TitleLike('Foobar')
	
	assert title_like.starts_with('Foo')


def test_ends_with():
	title_like = TitleLike('Foobar')
	
	assert title_like.ends_with('bar')


def test_extract_start():
	title_like = TitleLike('Lorem ipsum')
	title_like.extract(6)
	
	assert title_like == 'ipsum'


def test_extract_start_end():
	title_like = TitleLike('Lorem ipsum')
	title_like.extract(4, 7)
	
	assert title_like == 'm i'


def test_find_index():
	title_like = TitleLike('Foobar')
	
	assert title_like.find_index('o') == 1


def test_find_index_not_found():
	title_like = TitleLike('Foobar')
	
	assert title_like.find_index('z') is None


def test_remove_unicode_bidirectional_marks():
	title_like = TitleLike('Foobar\u200E\u202Abaz qux')
	title_like.remove_unicode_bidirectional_marks()
	
	assert title_like == 'Foobarbaz qux'


def test_collapse_whitespaces_series():
	title_like = TitleLike('Foo    bar')
	title_like.collapse_whitespaces_series()
	
	assert title_like == 'Foo bar'


def test_strip_surrounding_spaces():
	title_like = TitleLike('  Lorem  ')
	title_like.strip_surrounding_spaces()
	
	assert title_like == 'Lorem'


def test_sanitize():
	title_like = TitleLike(' _ FoO  : this/is A__/talk page _ ')
	title_like.sanitize()
	
	assert title_like == 'FoO : this/is A /talk page'


def test_split_by_first_colon_left_side():
	title_like = TitleLike('Foo_  :_Bar')
	first, second = title_like.split_by_first_colon()
	
	assert (first, second) == ('Foo_', '_Bar')


def test_split_by_first_colon_right_side():
	title_like = TitleLike('Foo_:  _Bar')
	first, second = title_like.split_by_first_colon()
	
	assert (first, second) == ('Foo_', '_Bar')


def test_split_by_first_colon_both_sides():
	title_like = TitleLike('Foo _  :  _Bar')
	first, second = title_like.split_by_first_colon()
	
	assert (first, second) == ('Foo _', '_Bar')


def test_split_by_first_colon_no_colons():
	title_like = TitleLike('Foobar')
	first, second = title_like.split_by_first_colon()
	
	assert (first, second) == (None, 'Foobar')


def test_contains_url_encoded_character():
	title_like = TitleLike('Foo%20bar')
	
	assert title_like.contains_url_encoded_character() is True


def test_contains_html_entity_like():
	title_like = TitleLike('foo&bar;baz')
	
	assert title_like.contains_html_entity_like() is True


@pytest.mark.parametrize('string', [
	'.', '..',
	'./Foobar', '../Foobar',
	'Foo/./Bar', 'Foo/../Bar',
	'Foobar/.', 'Foobar/..'
])
def test_has_relative_path_component_true(string):
	title_like = TitleLike(string)
	
	assert title_like.has_relative_path_component() is True


@pytest.mark.parametrize('string', [
	'Foobar'
])
def test_has_relative_path_component_false(string):
	title_like = TitleLike(string)
	
	assert title_like.has_relative_path_component() is False


@pytest.mark.parametrize('string', [
	'Username ~~~',
	'Signature ~~~~',
	'Timestamp ~~~~~',
])
def test_contains_signature_component(string):
	title_like = TitleLike(string)
	
	assert title_like.contains_signature_component() is True


@pytest.mark.parametrize('string, expected', [
	('Foo#Bar', 'Foo'),
	('Foo   # Bar   # ', 'Foo')
])
def test_remove_fragment(string, expected):
	title_like = TitleLike(string)
	title_like.remove_fragment_if_any()
	
	assert title_like == expected
