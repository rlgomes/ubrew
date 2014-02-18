"""
Boom! is a simple command line tool to send some load to a web app.

https://github.com/tarekziade/boom
"""

from ubrew.app import GitSourceRecipe, SetuptoolsRecipe

class BoomRecipe(GitSourceRecipe, SetuptoolsRecipe):

    name = 'boom'

    def __init__(self):
        GitSourceRecipe.__init__(self, 'git://github.com/tarekziade/boom')
        SetuptoolsRecipe.__init__(self)

