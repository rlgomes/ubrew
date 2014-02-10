"""
URL: https://github.com/jkbr/httpie
HTTPie is a command line HTTP client for humans
"""

from ubrew.app import UBrewAppGitSource, UBrewAppSetuptools


class UBrewApp(UBrewAppGitSource, UBrewAppSetuptools):

    def __init__(self):
        UBrewAppGitSource.__init__(self, 'git://github.com/jkbr/httpie')
        UBrewAppSetuptools.__init__(self)

