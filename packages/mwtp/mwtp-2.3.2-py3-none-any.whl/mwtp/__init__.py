'''Parser for MediaWiki titles'''

from .namespace import Namespace
from .parser import Parser as TitleParser
from .title import Title


__all__ = [
	'Namespace',
	'TitleParser',
	'Title'
]
