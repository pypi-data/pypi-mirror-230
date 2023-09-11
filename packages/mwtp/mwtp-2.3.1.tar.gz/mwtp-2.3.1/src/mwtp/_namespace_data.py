from dataclasses import dataclass, field


@dataclass(eq = False, frozen = True, kw_only = True, slots = True)
class NamespaceData:
	id: int
	case: str
	name: str
	subpages: bool
	content: bool
	nonincludable: bool
	canonical: str | None = field(default = None)
	aliases: set[str] = field(default_factory = set)
	namespaceprotection: str | None = field(default = None)
	defaultcontentmodel: str | None = field(default = None)
