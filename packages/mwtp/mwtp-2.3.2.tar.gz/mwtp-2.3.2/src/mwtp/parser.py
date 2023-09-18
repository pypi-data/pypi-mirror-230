import re
from typing import ClassVar, Literal, Mapping, Sequence, TypedDict

from ._alias_record import AliasRecord, NamespaceAlias
from ._namespace_data import NamespaceData
from ._namespace_id_map import NamespaceIDMap
from ._php_to_upper_map import PHP_TO_UPPER_MAP
from ._title_like import TitleLike
from .exceptions import (
	TitleContainsHTMLEntity,
	TitleContainsIllegalCharacter,
	TitleContainsSignatureComponent,
	TitleContainsURLEncodedCharacter,
	TitleHasRelativePathComponent,
	TitleHasSecondLevelNamespace,
	TitleIsBlank,
	TitleIsTooLong,
	TitleStartsWithColon
)
from .namespace import Namespace
from .title import Title


CasingRule = Literal['first-letter', 'case-sensitive']


class NamespaceDataAlwaysPresent(TypedDict):
	id: int
	case: CasingRule
	name: str
	subpages: bool
	content: bool
	nonincludable: bool


class NamespaceDataMayNotPresent(TypedDict, total = False):
	canonical: str
	namespaceprotection: str
	defaultcontentmodel: str


class NamespaceDataFromAPI(
	TypedDict,
	NamespaceDataAlwaysPresent,
	NamespaceDataMayNotPresent
):
	pass


class NamespaceDataFromAPIWithAliases(NamespaceDataFromAPI):
	aliases: set[str]


class Parser:
	'''
	A parser that parse strings using
	(mostly) data provided by the user.
	'''
	
	__slots__ = ('_namespace_data', '_namespace_id_map')
	
	_TITLE_MAX_BYTES: ClassVar[int] = \
		255
	_ILLEGAL_TITLE_CHARACTER: ClassVar[re.Pattern[str]] = \
		re.compile(r'''[\u0000-\u001F#<>[\]{|}\u007F\uFFFD]''')
	_TO_UPPER_MAP: ClassVar[dict[int, int]] = \
		PHP_TO_UPPER_MAP
	
	_namespace_data: dict[str, NamespaceData]
	_namespace_id_map: NamespaceIDMap
	
	def __init__(
		self,
		namespace_data: Mapping[str, NamespaceDataFromAPI],
		alias_entries: Sequence[NamespaceAlias]
	) -> None:
		'''
		Construct a new parser object from the given data.

		:param namespace_data: \
			A ``Mapping`` that maps string IDs to corresponding namespace data.
		:param alias_entries: A ``Sequence`` consisting of alias entries.
		'''
		
		self._namespace_data = {}
		self._namespace_id_map = NamespaceIDMap()
		
		alias_record = AliasRecord(alias_entries)
		
		self._initialize_data_record(namespace_data, alias_record)
		self._initialize_namespace_map()
	
	def _initialize_data_record(
		self,
		namespace_data: Mapping[str, NamespaceDataFromAPI],
		alias_record: AliasRecord
	) -> None:
		'''
		Convert all dicts in ``namespace_data`` to
		:class:`_dcs.NamespaceData`.

		:param namespace_data: The same data passed to :meth:`__init__`.
		:param alias_record: \
			An AliasRecord constructed
			using :meth:`__init__`'s alias_entries.
		'''
		
		for namespace_id, entry in namespace_data.items():
			aliases = alias_record[namespace_id]
			
			if aliases:
				self._namespace_data[namespace_id] = \
					NamespaceData(**entry, aliases = aliases)
			else:
				self._namespace_data[namespace_id] = \
					NamespaceData(**entry)
	
	def _initialize_namespace_map(self) -> None:
		'''
		Initialize a namespace-name-(alias)-to-ID map from given data.
		'''
		
		for namespace in self._namespace_data.values():
			keys_to_be_added = [namespace.name]
			keys_to_be_added.extend(namespace.aliases)
			
			if namespace.canonical:
				keys_to_be_added.append(namespace.canonical)
			
			for key in keys_to_be_added:
				self._namespace_id_map[key] = namespace.id
	
	@property
	def namespace_data(self) -> dict[str, NamespaceData]:
		'''
		The data given to and sanitized by the parser.
		'''
		
		return self._namespace_data
	
	def parse(self, string: str) -> Title:
		'''
		The main parsing method. Raises a subclass of
		:class:`.InvalidTitle` if the string is not
		a valid title.

		:param string: The string to parse.
		:return: A :class:`Title <.title.Title>`, if parsed successfully.
		'''
		
		title_like = TitleLike(string)
		title_like.sanitize()
		
		if title_like.starts_with(':'):
			title_like.extract(1)
		
		title_like.remove_fragment_if_any()
		
		namespace, page_name = self._split_title(title_like)
		
		self._validate_characters(page_name)
		self._validate_page_name_length(TitleLike(page_name), namespace)
		
		return self._make_title(page_name, namespace)
	
	def _make_title(self, page_name: str, namespace: int) -> Title:
		'''
		Apply the correct casing rule and construct
		the title object from given data.

		:param page_name: The page name part of the title.
		:param namespace: The namespace of the title.
		:return: The title object.
		'''
		
		corresponding_namespace_data = self._namespace_data[str(namespace)]
		casing_rule = corresponding_namespace_data.case
		cased_page_name = self._apply_casing_rule(page_name, casing_rule)
		
		return Title(
			name = cased_page_name,
			namespace = namespace,
			parser = self
		)
	
	@staticmethod
	def _apply_casing_rule(page_name: str, casing_rule: str) -> str:
		'''
		Apply the casing rule to the given page name.
		
		:param page_name: The page name to be cased.
		:param casing_rule: The casing rule to be applied.
		:return: The page name, cased.
		'''
		
		if casing_rule == 'case-sensitive':
			cased_page_name = page_name
		
		elif casing_rule == 'first-letter':
			first_character, the_rest = page_name[0], page_name[1:]
			first_character_code = ord(first_character)
			
			if first_character_code not in PHP_TO_UPPER_MAP:
				uppercased_first_char = first_character.upper()
			else:
				uppercased_first_char = \
					first_character.translate(PHP_TO_UPPER_MAP)
			
			cased_page_name = uppercased_first_char + the_rest
		
		else:
			raise TypeError(f'Case rule unrecognized: {casing_rule}')
		
		return cased_page_name
	
	def _split_title(self, title_like: TitleLike) -> tuple[int, str]:
		'''
		Split the given title into two parts: namespace and page name.

		:param title_like: The :class:``TitleLike`` object to be split.
		:return: A tuple consisting of the namespace and the page name.
		'''
		
		if title_like.starts_with(':'):
			raise TitleStartsWithColon
		
		namespace, page_name = title_like.split_by_first_colon()
		
		if namespace is not None:
			namespace_id = self._namespace_id_map[namespace]
		else:
			namespace_id = None
		
		if page_name == '':
			raise TitleIsBlank
		
		if page_name.startswith(':'):
			raise TitleStartsWithColon
		
		if namespace is None or namespace_id is None:
			return int(Namespace.MAIN), page_name
		
		if namespace_id != Namespace.TALK or ':' not in page_name:
			return namespace_id, page_name
		
		self._validate_second_level_namespace(page_name)
		
		return namespace_id, page_name
	
	def _validate_second_level_namespace(self, page_name: str) -> None:
		'''
		Raise an exception if the given page name
		starts with a valid namespace.
		
		:param page_name: The page name to validate.
		'''
		
		title_like = TitleLike(page_name)
		second_level_namespace, _ = title_like.split_by_first_colon()
		
		if not second_level_namespace:
			return
		
		if second_level_namespace in self._namespace_id_map:
			raise TitleHasSecondLevelNamespace
	
	def _validate_characters(self, page_name: str) -> None:
		'''
		Checks if ``page_name`` contains any illegal characters
		or components. May raise the following exceptions:

		* :class:`TitleContainsIllegalCharacters`
		* :class:`TitleContainsURLEncodedCharacters`
		* :class:`TitleContainsHTMLEntities`
		* :class:`TitleHasRelativePathComponents`
		* :class:`TitleContainsSignatureComponents`

		:param page_name: The page name to validate.
		'''
		
		title_like = TitleLike(page_name)
		
		if self._ILLEGAL_TITLE_CHARACTER.search(page_name):
			raise TitleContainsIllegalCharacter
		
		if title_like.contains_url_encoded_character():
			raise TitleContainsURLEncodedCharacter
		
		if title_like.contains_html_entity_like():
			raise TitleContainsHTMLEntity
		
		if title_like.has_relative_path_component():
			raise TitleHasRelativePathComponent
		
		if title_like.contains_signature_component():
			raise TitleContainsSignatureComponent
	
	def _validate_page_name_length(
		self,
		title_like: TitleLike,
		namespace: int
	) -> None:
		'''
		Raise :class:`TitleIsTooLong <.exceptions.TitleIsTooLong>`
		if the title is not in ``Special:`` namespace and
		its length exceeds :attr:`_TITLE_MAX_BYTES`.

		:param title_like: The :class:`TitleLike` object to be checked.
		:param namespace: The namespace of the title.
		'''
		
		not_a_special_page = namespace != Namespace.SPECIAL
		exceeds_max_byte_length = len(title_like) > self._TITLE_MAX_BYTES
		
		if not_a_special_page and exceeds_max_byte_length:
			raise TitleIsTooLong
