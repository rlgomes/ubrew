"""
"""

from ubrew.app import UBrewAppGitSource, UBrewAppMakeBuild


class UBrewApp(UBrewAppGitSource, UBrewAppMakeBuild):

    def __init__(self):
        UBrewAppGitSource.__init__(self, 'git://github.com/npm/npm')
        UBrewAppMakeBuild.__init__(self)

    def activate(self, install_directory):
        return {
                'PATH' : '%s/bin' % install_directory
               }

