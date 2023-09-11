from typing import Sequence, TypedDict


class NamespaceAlias(TypedDict):
	id: int
	alias: str


class AliasRecord:
	'''
	A record that maps namespace identifiers to their corresponding aliases.
	'''
	
	_record: dict[int, set[str]]
	
	def __init__(self, data: Sequence[NamespaceAlias]) -> None:
		self._record = {}
		
		for entry in data:
			namespace_id, alias = entry['id'], entry['alias']
			self._record.setdefault(namespace_id, set()).add(alias)
	
	def __getitem__(self, key: int | str) -> set[str] | None:
		numeric_key = int(key)
		
		return self._record.get(numeric_key)
	
	def __repr__(self) -> str:
		return f'{self.__class__.__name__}{self._record!r}'
