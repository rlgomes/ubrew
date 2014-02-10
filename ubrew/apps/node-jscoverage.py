"""
"""

from ubrew.app import UBrewAppGitSource, UBrewAppMakeBuild


class UBrewApp(UBrewAppGitSource, UBrewAppMakeBuild):

    def __init__(self):
        UBrewAppGitSource.__init__(self, 'git://github.com/visionmedia/node-jscoverage')
        UBrewAppMakeBuild.__init__(self)


    def available(self):
        return {
                '1.0' : {
                    'url': 'git://github.com/visionmedia/node-jscoverage'
                },
               }
        
    def activate(self, install_directory):
        return {
                'PATH' : '%s/bin' % install_directory
               }


