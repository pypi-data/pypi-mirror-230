"""
	text2story.core.exceptions

	All defined exceptions raised by the package.
"""

class InvalidLanguage(Exception):
	"""
	Raised if the user specified an invalid/unsupported language.
	"""
	def __init__(self, lang):
		description = ('Invalid language :' + lang)
		
		super().__init__(description)

class InvalidTool(Exception):
	"""
	Raised if the user specified an invalid/unsupported tool.
	"""

	def __init__(self, tool):
		description = ('Invalid tool: ' + tool)
		
		super().__init__(description)


class InvalidLink(Exception):
	"""
	Raised if the user specified an invalid/unsupported tool.
	"""

	def __init__(self, link):
		description = ('Invalid link: ' + link)

		super().__init__(description)

class InvalidIDAnn(Exception):
	"""
	Raised if the user specified an invalid/unsupported tool.
	"""

	def __init__(self, entity_id):
		description = ('Invalid id: ' + entity_id)

		super().__init__(description)

class UninstalledModel(Exception):
    """
	Raised if the given model was not installed
    """

    def __init__(self, model_name, command):
        description = ('The follwing model was not installed: ' + model_name + \
					   '\n You should use the following command to install: ' + command)

        super().__init__(description)