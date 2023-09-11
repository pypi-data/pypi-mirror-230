import pytest

from mwtp._alias_record import AliasRecord


@pytest.fixture(scope = 'session')
def enwiki_alias_record(en_wikipedia_data):
	alias_record = AliasRecord(en_wikipedia_data['namespacealiases'])
	
	yield alias_record


def test_repr(enwiki_alias_record):
	assert isinstance(repr(enwiki_alias_record), str)
