"""
Boom! is a simple command line tool to send some load to a web app.
https://github.com/tarekziade/boom
"""

from ubrew.app import UBrewAppGitSource, UBrewAppSetuptools

class UBrewApp(UBrewAppGitSource, UBrewAppSetuptools):

    def __init__(self):
        UBrewAppGitSource.__init__(self, 'git://github.com/tarekziade/boom')
        UBrewAppSetuptools.__init__(self)

