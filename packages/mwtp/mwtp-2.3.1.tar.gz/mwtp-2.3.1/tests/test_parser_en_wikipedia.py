import pytest

from mwtp.exceptions import (
	TitleContainsHTMLEntity, TitleContainsIllegalCharacter, TitleContainsSignatureComponent,
	TitleContainsURLEncodedCharacter, TitleHasRelativePathComponent, TitleHasSecondLevelNamespace, TitleIsBlank,
	TitleIsTooLong, TitleStartsWithColon
)
from mwtp.title import Title


@pytest.fixture(scope = 'module')
def parser(en_wikipedia_parser):
	yield en_wikipedia_parser


@pytest.mark.parametrize('string, expected', [
	### Plain
	('Foobar', 'Foobar'),
	('.com', '.com'),
	
	### With fragments
	('Foo#bar', 'Foo'),
	('Talk:  fOo # bar', 'Talk:FOo'),
	('Foo   #  __  bar  __ ', 'Foo'),
	('Foo&#23;bar', 'Foo&'),
	('pRoJecT _:_ foo&#123;bar', 'Wikipedia:Foo&'),
	
	### Quotes
	('Foo "bar"', 'Foo "bar"'),
	("Foo 'Bar'", "Foo 'Bar'"),
	('"', '"'),
	("'", "'"),
	
	### Tildes
	('~', '~'),
	('~~', '~~'),
	('Foo~~', 'Foo~~'),
	
	### With namespace prefixes
	('Talk:Foobar', 'Talk:Foobar'),
	('TaLk_:_Foo _: Bar', 'Talk:Foo : Bar'),
	('fiLe _:__ Foo _.svg', 'File:Foo .svg'),
	('FilE__ __talk:bAr.svg', 'File talk:BAr.svg'),
	
	### Barely relative path components
	('.../Foobar', '.../Foobar'),
	('Foo/.../Bar', 'Foo/.../Bar'),
	('Foobar/...', 'Foobar/...'),
	
	### Single leading colon
	(':Foobar', 'Foobar'),
	('___:_ __ __fOoBar', 'FOoBar'),
	
	### Length
	(f'catEgOry  _:_ {"W" * 255}', f'Category:{"W" * 255}'),
	('W' * 255, 'W' * 255),
	(f'File :___{"W" * 232}.jpeg', f'File:{"W" * 232}.jpeg'),
	
	### Case-sensitive
	('Gadget:foo', 'Gadget:foo'),
	('gAdget  _ :_ _ fOo', 'Gadget:fOo'),
	
	### Unicode uppercase
	('ß is ss', 'ß is ss'),
	('ᾇ', 'ᾏ'),
	
	### Unipain
	('\ud81b\ude7ffoo', '\ud81b\ude7ffoo'),
	('𖹿foo', '𖹿foo')
])
def test_parse_valid_title(parser, string, expected):
	title = parser.parse(string)
	
	assert isinstance(title, Title)
	assert title.full_name == expected


@pytest.mark.parametrize('string', [
	'', ':', '__  __', '  __  ',
	'Talk:', 'Category: ', 'Category: #bar'
])
def test_parse_blank_title(parser, string):
	with pytest.raises(TitleIsBlank):
		parser.parse(string)


@pytest.mark.parametrize('string', [
	'A [ B', 'A ] B', 'A { B', 'A } B', 'A < B', 'A > B',
	'A | B', 'A \t B', 'A \n B',
	'Foo\uFFFDbar'
])
def test_parse_illegal_character(parser, string):
	with pytest.raises(TitleContainsIllegalCharacter):
		parser.parse(string)


@pytest.mark.parametrize('string', [
	'Foo%20bar', 'Foo%23bar', 'Foo%2523bar'
])
def test_parse_url_encoded_character(parser, string):
	with pytest.raises(TitleContainsURLEncodedCharacter):
		parser.parse(string)


@pytest.mark.parametrize('string', [
	'Foo&eacute;bar', 'Foo&nbsp;bar',
	'Foo&nonexistententity;bar'
])
def test_parse_html_entity(parser, string):
	with pytest.raises(TitleContainsHTMLEntity):
		parser.parse(string)


@pytest.mark.parametrize('string', [
	'Talk:Category:Foobar',
	'Talk:File:Foobar.svg',
	'_ TaLk_: tAlK: Fooboo',
	' _ TALk: ___ project: foo'
])
def test_parse_second_level_namespace(parser, string):
	with pytest.raises(TitleHasSecondLevelNamespace):
		parser.parse(string)


@pytest.mark.parametrize('string', [
	'.', '..',
	'./Foobar', '../Foobar',
	'Foo/./Bar', 'Foo/../Bar',
	'Foobar/.', 'Foobar/..'
])
def test_parse_relative_path_component(parser, string):
	with pytest.raises(TitleHasRelativePathComponent):
		parser.parse(string)


@pytest.mark.parametrize('string', [
	'Username ~~~',
	'Signature ~~~~',
	'Timestamp ~~~~~'
])
def test_parse_signature_component(parser, string):
	with pytest.raises(TitleContainsSignatureComponent):
		parser.parse(string)


@pytest.mark.parametrize('string', [
	'::Foo',
	': _:_Bar',
	'Talk: : Foobar',
	'Project___:: Foobar'
])
def test_parse_leading_colon(parser, string):
	with pytest.raises(TitleStartsWithColon):
		parser.parse(string)


@pytest.mark.parametrize('string', [
	'w' * 256,
	'À' * 128,
	'维' * 85 + 'k',
	'w' * 252 + '.jpeg',
	'À' * 126 + '.jpeg',
	'维' * 85 + '.jpeg'
])
def test_parse_lengthy_page_name(parser, string):
	with pytest.raises(TitleIsTooLong):
		parser.parse(string)
