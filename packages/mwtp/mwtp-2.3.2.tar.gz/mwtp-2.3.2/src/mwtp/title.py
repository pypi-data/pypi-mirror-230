from __future__ import annotations

import re
from functools import total_ordering
from typing import ClassVar, TYPE_CHECKING, TypeVar

from ._namespace_data import NamespaceData
from .namespace import Namespace


if TYPE_CHECKING:
	from .parser import Parser

Self = TypeVar('Self', bound = 'Title')


@total_ordering
class Title:
	'''
	Represents a MediaWiki title.

	This class is not meant to be used directly.
	Use :meth:`Parser.parse <.parser.Parser.parse>` instead.
	'''
	
	__slots__ = ('_name', '_namespace', '_parser')
	
	_extension: ClassVar[re.Pattern[str]] = \
		re.compile(r'(?<=\.)[^.\s]+$')
	
	_parser: Parser
	_name: str
	_namespace: int
	
	def __init__(self, name: str, *, namespace: int, parser: Parser) -> None:
		'''
		Construct a Title object.

		:param name: The page name part of the title.
		:param namespace: The namespace of the title.
		:param parser: The parser which constructed the title.
		'''
		
		self._name = name
		self._namespace = namespace
		self._parser = parser
	
	def __str__(self) -> str:
		return self.full_name
	
	def __repr__(self) -> str:
		return f'{self.__class__.__name__}({self.full_name!r})'
	
	def __hash__(self) -> int:
		return hash(self.full_name)
	
	def __lt__(self, other: object) -> bool:
		if isinstance(other, Title):
			return self.full_name < other.full_name
		
		if isinstance(other, str):
			return self.full_name < other
		
		return NotImplemented
	
	def __eq__(self, other: object) -> bool:
		if isinstance(other, Title):
			return self.full_name == other.full_name
		
		if isinstance(other, str):
			return self.full_name == other
		
		return NotImplemented
	
	def __add__(self, other: str) -> Title:
		'''
		Add a string to this title's full name
		and pass that to the parser.
		
		A :class:`Title` cannot be added to one another
		since there is no way to determine the namespace
		of the new title.
		'''
		
		if not isinstance(other, str):
			return NotImplemented
		
		return self._parser.parse(f'{self}{other}')
	
	def __truediv__(self, other: str) -> Title:
		'''
		Add ``/`` and ``other`` to the title
		and pass that to the parser.
		'''
		
		return self + f'/{other}'
	
	@property
	def full_name(self) -> str:
		'''
		The full title (i.e. ``Namespace:Pagename`` or ``Pagename``).
		'''
		
		if self.namespace != 0:
			return f'{self.namespace_name}:{self._name}'
		
		return self.name
	
	@property
	def namespace(self) -> int:
		'''
		The title's namespace ID.
		'''
		
		return self._namespace
	
	@property
	def name(self) -> str:
		'''
		The title without the namespace.
		'''
		
		return self._name
	
	@property
	def namespace_name(self) -> str:
		'''
		The localized name of the title's namespace.
		'''
		
		return self.namespace_data.name
	
	@property
	def namespace_data(self) -> NamespaceData:
		'''
		An object containing all known information
		about the title's namespace.
		This is retrieved from the parser.
		'''
		
		return self._parser.namespace_data[str(self.namespace)]
	
	@property
	def canonical_namespace_name(self) -> str | None:
		'''
		The canonical name of the title's namespace.
		'''
		
		return self.namespace_data.canonical
	
	@property
	def associated_namespace(self) -> int | None:
		'''
		The ID of the talk or subject namespace to which
		the title's namespace is associated with.
		'''
		
		if self.namespace < 0:
			return None
		
		if self.namespace % 2 == 1:
			return self.namespace - 1
		else:
			return self.namespace + 1
	
	@property
	def associated_namespace_name(self) -> str | None:
		'''
		The localized name of the title's associated namespace.
		'''
		
		namespace_data = self.associated_namespace_data
		
		if namespace_data is None:
			return None
		
		return namespace_data.name
	
	@property
	def associated_namespace_data(self) -> NamespaceData | None:
		'''
		An object containing all known information about
		the title's associated namespace or ``None`` if there
		is no such namespace.
		This is retrieved from the parser.
		'''
		
		namespace_id = self.associated_namespace
		
		if namespace_id is None:
			return None
		
		return self._parser.namespace_data \
			.get(str(namespace_id))
	
	@property
	def in_content_namespace(self) -> bool:
		'''
		Whether the namespace of the title is a content namespace.
		'''
		
		return self.namespace_data.content
	
	@property
	def fragments(self) -> list[str]:
		'''
		If the namespace has ``.subpages == True``,
		return a list of strings generated from
		splitting the title by ``/``. Else,
		return the name wrapped in a list.
		'''
		
		if self.namespace_data.subpages:
			return self.name.split('/')
		
		return [self.name]
	
	@property
	def root(self: Self) -> Self:
		'''
		A Title object representing the root title
		of this title.
		'''
		
		return self.__class__(
			self.fragments[0],
			namespace = self.namespace,
			parser = self._parser
		)
	
	@property
	def base(self: Self) -> Self:
		'''
		A Title object representing the parent title
		of this title.
		'''
		
		fragments = self.fragments
		
		if len(fragments) == 1:
			new_page_name = fragments[0]
		else:
			new_page_name = '/'.join(fragments[:-1])
		
		return self.__class__(
			new_page_name,
			namespace = self.namespace,
			parser = self._parser
		)
	
	@property
	def tail(self) -> str:
		'''
		The rightmost fragment of the title.
		'''
		# Naming reason: https://superuser.com/q/524724
		
		return self.fragments[-1]
	
	@property
	def is_subpage(self) -> bool:
		'''
		Whether the title has a parent title.
		'''
		
		return len(self.fragments) > 1
	
	@property
	def extension(self) -> str | None:
		'''
		The extension part of a file name, if any.
		'''
		
		if self.namespace not in (Namespace.FILE, Namespace.FILE_TALK):
			return None
		
		match = self._extension.search(self.name)
		
		if match is None:
			return None
		
		return match.group(0)
	
	@property
	def associated(self: Self) -> Self | None:
		'''
		The title associated to this title, or ``None``
		if there is no such title.
		'''
		
		associated_namespace = self.associated_namespace
		
		if associated_namespace is None:
			return None
		
		return self.__class__(
			self.name,
			namespace = associated_namespace,
			parser = self._parser
		)
	
	@property
	def subject(self: Self) -> Self:
		'''
		The subject title correspond to this title.
		Can be itself if it is a subject title.
		'''
		
		associated = self.associated
		
		if associated is None:
			return self
		
		if associated.namespace % 2 == 1:
			return self
		
		return associated
	
	@property
	def talk(self: Self) -> Self | None:
		'''
		The talk title correspond to this title,
		or ``None`` if there is no such title.
		'''
		
		if self.namespace < 0:
			return None
		
		if self.namespace % 2 == 1:
			return self
		
		return self.associated
