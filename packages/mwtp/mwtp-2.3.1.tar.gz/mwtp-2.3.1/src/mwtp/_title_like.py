import re
from typing import ClassVar, Optional, SupportsIndex


class TitleLike:
	'''
	A thin wrapper around a string, providing some convenient methods
	for formatting and validating it.

	Meant to be used internally.
	'''
	
	_whitespace_char_codes: ClassVar[list[int]] = [
		0x0020, 0x005F, 0x00A0, 0x1680, 0x180E,
		0x2000, 0x2001, 0x2002, 0x2003, 0x2004,
		0x2006, 0x2007, 0x2008, 0x2009, 0x200A,
		0x2028, 0x2029, 0x202F, 0x205F, 0x3000
	]
	_unicode_bidi_char_codes: ClassVar[list[int]] = [
		0x200E, 0x200F, 0x202A, 0x202E
	]
	
	_whitespace_series: ClassVar[re.Pattern[str]] = \
		re.compile(f'[{"".join(map(chr, _whitespace_char_codes))}]+')
	_unicode_bidi_marks: ClassVar[re.Pattern[str]] = \
		re.compile(f'[{"".join(map(chr, _unicode_bidi_char_codes))}]+')
	
	_first_colon: ClassVar[re.Pattern[str]] = \
		re.compile(f' *: *')
	_url_encoded_char: ClassVar[re.Pattern[str]] = \
		re.compile(r'%[\dA-Fa-f]{2}')
	_html_entity_like: ClassVar[re.Pattern[str]] = \
		re.compile(r'&[\dA-Za-z\u0080-\uFFFF]+;')
	
	_disallowed_leading_components: ClassVar[list[str]] = \
		['./', '../']
	_disallowed_trailing_components: ClassVar[list[str]] = \
		['/.', '/..']
	_disallowed_components: ClassVar[list[str]] = \
		['/./', '/../']
	
	def __init__(self, string: str) -> None:
		self._string = string
	
	def __contains__(self, item: str) -> bool:
		return item in self._string
	
	def __eq__(self, other: object) -> bool:
		if isinstance(other, TitleLike):
			return str(self) == str(other)
		
		if isinstance(other, str):
			return str(self) == other
		
		return NotImplemented
	
	def __getitem__(self, item: SupportsIndex | slice) -> str:
		return self._string[item]
	
	def __len__(self) -> int:
		surrogate_pair_converted = self._string \
			.encode('utf-16-be', 'surrogatepass') \
			.decode('utf-16-be')
		
		return len(surrogate_pair_converted.encode('utf-8'))
	
	def __repr__(self) -> str:
		return f'{self.__class__.__name__}({self._string!r})'
	
	def __str__(self) -> str:
		return self._string
	
	def set(self, new_value: str) -> None:
		'''
		Set a new value for the string.

		:param new_value: The new value.
		'''
		
		self._string = new_value
	
	def starts_with(self, substring: str) -> bool:
		'''
		Whether the string starts with the given substring.

		:param substring: The substring to be checked.
		'''
		
		return self._string.startswith(substring)
	
	def ends_with(self, substring: str) -> bool:
		'''
		Whether the string ends with the given substring.

		:param substring: The substring to be checked.
		'''
		
		return self._string.endswith(substring)
	
	def extract(self, start: int, end: Optional[int] = None) -> None:
		'''
		Take a slice of the string from start (inclusive) to end (exclusive)
		and set that as the new string.

		:param start: The start index (inclusive).
		:param end: The end index (exclusive), defaults to ``None``.
		'''
		
		self._string = self._string[start:end]
	
	def find_index(self, substring: str) -> int | None:
		'''
		Return the first index at which the substring is found
		or None if there is no such index.

		:param substring: The substring to search for.
		'''
		
		index = self._string.find(substring)
		
		return index if index != -1 else None
	
	def remove_unicode_bidirectional_marks(self) -> None:
		'''
		Remove all Unicode bidirectional characters.
		'''
		
		self._string = self._unicode_bidi_marks.sub('', self._string)
	
	def collapse_whitespaces_series(self) -> None:
		'''
		Collapse every whitespace/underscore sequence into a single space.
		'''
		
		self._string = self._whitespace_series.sub(' ', self._string)
	
	def strip_surrounding_spaces(self) -> None:
		'''
		Remove leading and trailing spaces.
		'''
		
		self._string = self._string.strip(' ')
	
	def sanitize(self) -> None:
		'''
		Shorthand for the following methods:

		* :meth:`remove_unicode_bidirectional_marks`
		* :meth:`collapse_whitespaces_series`
		* :meth:`strip_surrounding_underscore`
		'''
		
		self.remove_unicode_bidirectional_marks()
		self.collapse_whitespaces_series()
		self.strip_surrounding_spaces()
	
	def split_by_first_colon(self) -> tuple[str | None, str]:
		'''
		Split the string by the first colon and any surrounding
		spaces and return a tuple consisting of two string elements.

		If there is no colon, the first element will be None.

		Does not modify the original string.
		'''
		
		splitted = self._first_colon.split(self._string, maxsplit = 1)
		
		if len(splitted) == 2:
			return splitted[0], splitted[1]
		
		return None, splitted[0]
	
	def contains_url_encoded_character(self) -> bool:
		'''
		Whether the string has a URL encoded character.
		'''
		
		match = self._url_encoded_char.search(self._string)
		
		return match is not None
	
	def contains_html_entity_like(self) -> bool:
		'''
		Whether the string contains something that
		looks like an HTML entity.
		'''
		
		match = self._html_entity_like.search(self._string)
		
		return match is not None
	
	def has_relative_path_component(self) -> bool:
		'''
		Whether any of the following is true:

		* ``self == '.'``
		* ``self == '..'``
		* ``self.starts_with('./')``
		* ``self.starts_with('../')``
		* ``'/./' in self``
		* ``'/../' in self``
		* ``self.ends_with('/.')``
		* ``self.ends_with('/..')``
		'''
		
		if '.' not in self._string:
			return False
		
		looks_like_relative_path = \
			self._is_relative_path_component() or \
			self._starts_with_disallowed_component() or \
			self._contains_disallowed_component() or \
			self._ends_with_disallowed_component()
		
		return looks_like_relative_path
	
	def _is_relative_path_component(self) -> bool:
		'''
		Whether the string is either ``.`` or ``..``.
		'''
		
		return self._string == '.' or self._string == '..'
	
	def _starts_with_disallowed_component(self) -> bool:
		'''
		Whether the string starts with a disallowed component.
		'''
		
		return any(
			self.starts_with(component)
			for component in self._disallowed_leading_components
		)
	
	def _ends_with_disallowed_component(self) -> bool:
		'''
		Whether the string ends with a disallowed component.
		'''
		
		return any(
			self.ends_with(component)
			for component in self._disallowed_trailing_components
		)
	
	def _contains_disallowed_component(self) -> bool:
		'''
		Whether the string contains a disallowed component.
		'''
		
		return any(
			component in self
			for component in self._disallowed_components
		)
	
	def contains_signature_component(self) -> bool:
		'''
		Whether the string contains triple tildes (``~~~``).
		'''
		
		return '~~~' in self._string
	
	def remove_fragment_if_any(self) -> None:
		'''
		Remove the fragment part, if any.
		'''
		
		fragment_index = self.find_index('#')
		
		if fragment_index is not None:
			self.extract(0, fragment_index)
		
		self.strip_surrounding_spaces()
