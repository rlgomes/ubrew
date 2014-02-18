"""
"""

from ubrew.app import GitSourceRecipe, AutoconfRecipe


class NodeRecipe(GitSourceRecipe, AutoconfRecipe):

    name = 'node'

    def __init__(self):
        GitSourceRecipe.__init__(self, 'git://github.com/joyent/node')
        AutoconfRecipe.__init__(self)

    def use(self, install_directory):
        return {
                'PATH' : '%s/bin' % install_directory
               }

