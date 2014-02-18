"""
URL: https://github.com/jkbr/httpie
HTTPie is a command line HTTP client for humans
"""

from ubrew.app import GitSourceRecipe, SetuptoolsRecipe


class HttpieRecipe(GitSourceRecipe, SetuptoolsRecipe):

    name = 'httpie'

    def __init__(self):
        GitSourceRecipe.__init__(self, 'git://github.com/jkbr/httpie')
        SetuptoolsRecipe.__init__(self)

