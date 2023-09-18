from enum import IntEnum, unique


@unique
class Namespace(IntEnum):
	'''
	An :class:`IntEnum` that contains all default namespace IDs,
	from Media (-2) to Category talk (15).
	'''
	
	MEDIA = -2
	SPECIAL = -1
	MAIN = 0
	TALK = 1
	USER = 2
	USER_TALK = 3
	PROJECT = 4
	PROJECT_TALK = 5
	FILE = 6
	FILE_TALK = 7
	MEDIAWIKI = 8
	MEDIAWIKI_TALK = 9
	TEMPLATE = 10
	TEMPLATE_TALK = 11
	HELP = 12
	HELP_TALK = 13
	CATEGORY = 14
	CATEGORY_TALK = 15
