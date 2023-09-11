from typing import Iterator


class NamespaceIDMap:
	'''
	An object that maps namespace names to their corresponding IDs.
	'''
	
	_map: dict[str, int]
	
	def __init__(self) -> None:
		self._map = {}
	
	def __repr__(self) -> str:
		return f'{self.__class__.__name__}({self._map!r})'
	
	def __contains__(self, key: str) -> bool:
		return self[key] is not None
	
	def __getitem__(self, key: str) -> int | None:
		if not isinstance(key, str):
			raise TypeError('Key must be a string')
		
		normalized_key = key.lower()
		
		return self._map.get(normalized_key)
	
	def __setitem__(self, key: str, value: int) -> None:
		if not isinstance(key, str):
			raise TypeError('Key must be a string')
		
		if not isinstance(value, int):
			raise TypeError('Value must be an integer')
		
		normalized_key = key.lower()
		
		self._map[normalized_key] = value
	
	def __delitem__(self, key: str) -> None:
		raise TypeError('Keys cannot be deleted')
	
	def __len__(self) -> int:
		return len(self._map)
	
	def __iter__(self) -> Iterator[str]:
		return iter(self._map)
