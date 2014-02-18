"""
"""

from ubrew.app import GitSourceRecipe, AutoconfRecipe


class NPMRecipe(GitSourceRecipe, AutoconfRecipe):

    name = 'npm'

    def __init__(self):
        GitSourceRecipe.__init__(self, 'git://github.com/npm/npm')
        AutoconfRecipe.__init__(self)

    def use(self, install_directory):
        return {
                'PATH' : '%s/bin' % install_directory
               }

