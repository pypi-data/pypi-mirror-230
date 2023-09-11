import json
from copy import deepcopy
from pathlib import Path

import pytest

from mwtp import Title, TitleParser
from mwtp._namespace_data import NamespaceData


@pytest.fixture(scope = 'module')
def assets():
	assets = Path(__file__).resolve().parent / 'assets'
	
	yield assets


@pytest.fixture(scope = 'module')
def enwiki_parser(assets):
	with open(assets / 'en.wikipedia.org.json') as file:
		data = json.load(file)
	
	parser = TitleParser(data['namespaces'], data['namespacealiases'])
	
	yield parser


@pytest.fixture(scope = 'module')
def dewiki_parser(assets):
	with open(assets / 'de.wikipedia.org.json') as file:
		data = json.load(file)
	
	parser = TitleParser(data['namespaces'], data['namespacealiases'])
	
	yield parser


@pytest.fixture(scope = 'module')
def special_blank_page(enwiki_parser):
	title = enwiki_parser.parse('Special:BlankPage')
	
	yield title


@pytest.fixture(scope = 'module')
def loremipsum(enwiki_parser):
	title = enwiki_parser.parse('Lorem ipsum')
	
	yield title


@pytest.fixture(scope = 'module')
def talk_foobar(enwiki_parser):
	title = enwiki_parser.parse('Talk:Foobar')
	
	yield title


@pytest.fixture(scope = 'module')
def template_this_has_a_long_name(enwiki_parser):
	title = enwiki_parser.parse('Template:This/Has/A/Long/Name')
	
	yield title


@pytest.fixture(scope = 'module')
def user_talk_john_doe_archive(enwiki_parser):
	title = enwiki_parser.parse('User talk:John Doe/Archive')
	
	yield title


@pytest.fixture(scope = 'module')
def wikipedia_lorem_ipsum(enwiki_parser):
	title = enwiki_parser.parse('Wikipedia:Lorem/Ipsum')
	
	yield title


@pytest.fixture(scope = 'module')
def file_dolor_sit_amet_jpg(enwiki_parser):
	title = enwiki_parser.parse('File:Dolor/Sit/Amet.jpg')
	
	yield title


@pytest.fixture(scope = 'module')
def file_adipiscing_elit(enwiki_parser):
	title = enwiki_parser.parse('File:Adipiscing/Elit')
	
	yield title


@pytest.fixture(scope = 'module')
def category_barfoo(enwiki_parser):
	title = enwiki_parser.parse('Category:Barfoo')
	
	yield title


@pytest.fixture(scope = 'module')
def diskussion_foobar(dewiki_parser):
	title = dewiki_parser.parse('Diskussion:Foobar')
	
	yield title


def test_str(talk_foobar):
	assert str(talk_foobar) == 'Talk:Foobar'


def test_repr(talk_foobar):
	assert repr(talk_foobar) == "Title('Talk:Foobar')"


def test_hash(talk_foobar):
	assert hash(talk_foobar) == hash('Talk:Foobar')


def test_lt_title(talk_foobar, category_barfoo):
	assert category_barfoo < talk_foobar


def test_lt_str(talk_foobar):
	assert talk_foobar < 'User:Foobar'


def test_lt_other(talk_foobar):
	with pytest.raises(TypeError):
		_ = talk_foobar < {}


def test_eq_title(talk_foobar):
	talk_foobar_copied = deepcopy(talk_foobar)
	
	assert talk_foobar is not talk_foobar_copied
	assert talk_foobar == talk_foobar_copied


def test_eq_str(talk_foobar):
	assert talk_foobar == 'Talk:Foobar'


def test_add_str(talk_foobar):
	new_title = talk_foobar + ' bazqux'
	assert new_title.full_name == 'Talk:Foobar bazqux'


def test_add_non_str(talk_foobar, wikipedia_lorem_ipsum):
	with pytest.raises(TypeError):
		talk_foobar + wikipedia_lorem_ipsum


def test_truediv(talk_foobar):
	new_title = talk_foobar / 'Bazqux'
	assert new_title.full_name == 'Talk:Foobar/Bazqux'


def test_full_name(talk_foobar):
	assert talk_foobar.full_name == str(talk_foobar) == 'Talk:Foobar'


def test_namespace(talk_foobar):
	assert talk_foobar.namespace == 1


def test_name(talk_foobar):
	assert talk_foobar.name == 'Foobar'


def test_namespace_name(talk_foobar):
	assert talk_foobar.namespace_name == 'Talk'


def test_namespace_data(talk_foobar):
	assert isinstance(talk_foobar.namespace_data, NamespaceData)


def test_canonical_namespace_name(diskussion_foobar):
	assert diskussion_foobar.canonical_namespace_name == 'Talk'


def test_associated_namespace(category_barfoo):
	assert category_barfoo.associated_namespace == 15


def test_associated_namespace_no_subpage(special_blank_page):
	assert special_blank_page.associated_namespace is None


def test_associated_namespace_name(category_barfoo):
	assert category_barfoo.associated_namespace_name == 'Category talk'


def test_associated_namespace_name_main(talk_foobar):
	assert talk_foobar.associated_namespace_name == ''


def test_associated_namespace_name_no_subpage(special_blank_page):
	assert special_blank_page.associated_namespace_name is None


def test_associated_namespace_data(category_barfoo):
	assert isinstance(category_barfoo.associated_namespace_data, NamespaceData)


def test_associated_namespace_data_no_subpage(special_blank_page):
	assert special_blank_page.associated_namespace_data is None


def test_in_content_namespace(loremipsum):
	assert loremipsum.in_content_namespace is True


def test_fragments(wikipedia_lorem_ipsum):
	assert wikipedia_lorem_ipsum.fragments == ['Lorem', 'Ipsum']


def test_fragments_no_subpage(special_blank_page):
	new_title = special_blank_page / 'Foobar'
	assert new_title.fragments == ['BlankPage/Foobar']


def test_root(wikipedia_lorem_ipsum):
	root = wikipedia_lorem_ipsum.root
	
	assert isinstance(root, Title)
	assert root.full_name == 'Wikipedia:Lorem'


def test_root_no_subpage(special_blank_page):
	new_title = special_blank_page / 'Foobar'
	root = new_title.root
	
	assert isinstance(root, Title)
	assert root.full_name == 'Special:BlankPage/Foobar'


def test_base(template_this_has_a_long_name):
	base = template_this_has_a_long_name.base
	
	assert base.full_name == 'Template:This/Has/A/Long'


def test_base_no_subpage(file_dolor_sit_amet_jpg):
	base = file_dolor_sit_amet_jpg.base
	
	assert base.full_name == 'File:Dolor/Sit/Amet.jpg'


def test_tail(template_this_has_a_long_name):
	assert template_this_has_a_long_name.tail == 'Name'


def test_tail_no_subpage(file_dolor_sit_amet_jpg):
	assert file_dolor_sit_amet_jpg.tail == 'Dolor/Sit/Amet.jpg'


def test_is_subpage_false(loremipsum):
	assert loremipsum.is_subpage is False


def test_is_subpage_true(template_this_has_a_long_name):
	assert template_this_has_a_long_name.is_subpage is True


def test_is_subpage_no_subpage(file_dolor_sit_amet_jpg):
	assert file_dolor_sit_amet_jpg.is_subpage is False


def test_extension(file_dolor_sit_amet_jpg):
	assert file_dolor_sit_amet_jpg.extension == 'jpg'


def test_extension_not_a_file(wikipedia_lorem_ipsum):
	assert wikipedia_lorem_ipsum.extension is None


def test_extension_file_without_extension(file_adipiscing_elit):
	assert file_adipiscing_elit.extension is None


def test_extension_talk(file_dolor_sit_amet_jpg):
	assert file_dolor_sit_amet_jpg.associated.extension == 'jpg'


def test_associated(wikipedia_lorem_ipsum):
	associated = wikipedia_lorem_ipsum.associated
	
	assert associated.full_name == 'Wikipedia talk:Lorem/Ipsum'


def test_associated_virtual_namespace(special_blank_page):
	assert special_blank_page.associated is None


def test_subject(talk_foobar):
	assert talk_foobar.subject.full_name == 'Foobar'


def test_subject_virtual_namespace(special_blank_page):
	assert special_blank_page.subject is special_blank_page


def test_subject_subject_page(wikipedia_lorem_ipsum):
	assert wikipedia_lorem_ipsum.subject is wikipedia_lorem_ipsum


def test_talk(loremipsum):
	assert loremipsum.talk.full_name == 'Talk:Lorem ipsum'


def test_talk_virtual_namespace(special_blank_page):
	assert special_blank_page.talk is None


def test_talk_talk_page(user_talk_john_doe_archive):
	assert user_talk_john_doe_archive.talk is user_talk_john_doe_archive
