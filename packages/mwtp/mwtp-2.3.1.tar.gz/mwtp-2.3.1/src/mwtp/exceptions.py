class InvalidTitle(Exception):
	'''
	Umbrella exception for all kinds of exceptions
	a parser might raise.
	'''
	pass


class TitleContainsIllegalCharacter(InvalidTitle):
	'''
	Raised if the title contains illegal characters.
	'''
	
	def __init__(self) -> None:
		super().__init__('Title contains illegal characters')


class TitleContainsSignatureComponent(InvalidTitle):
	'''
	Raised if the title contains ``~~~``.
	'''
	
	def __init__(self) -> None:
		super().__init__('Title contains a signature component')


class TitleContainsURLEncodedCharacter(InvalidTitle):
	'''
	Raised if the title contains a URL-encoded character.
	'''
	
	def __init__(self) -> None:
		super().__init__('Title contains a URL-encoded character')


class TitleContainsHTMLEntity(InvalidTitle):
	'''
	Raised if the title contains an HTML entity or
	something that looks like one.
	'''
	
	def __init__(self) -> None:
		super().__init__('Title contains a HTML entity look-alike')


class TitleHasRelativePathComponent(InvalidTitle):
	'''
	Raised if the title contains a relative path component
	or only consists of either one or two dots.
	'''
	
	def __init__(self) -> None:
		super().__init__('Title contains a relative path component')


class TitleHasSecondLevelNamespace(InvalidTitle):
	'''
	Raised if the title is determined to be in the ``Talk:``
	namespace while also contains a second valid namespace.
	'''
	
	def __init__(self) -> None:
		super().__init__('Second level namespace cannot be resolved')


class TitleIsBlank(InvalidTitle):
	'''
	Raised if the title contains nothing but whitespaces
	and/or a leading colon.
	'''
	
	def __init__(self) -> None:
		super().__init__('Title is blank or only has the namespace part')


class TitleIsTooLong(InvalidTitle):
	'''
	Raised if the title's length exceed
	the maximum length of a title.
	'''
	
	def __init__(self) -> None:
		super().__init__('Title exceeds maximum length of 256 bytes')


class TitleStartsWithColon(InvalidTitle):
	'''
	Raised if the page name starts with a colon,
	or the namespace part starts with more than one colon.
	'''
	
	def __init__(self) -> None:
		super().__init__('Invalid colon at the start of namespace or page name')
