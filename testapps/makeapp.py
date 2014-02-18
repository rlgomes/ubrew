
from ubrew.app import AutoconfRecipe

import os

class MakeAppRecipe(AutoconfRecipe):

    name = 'makeapp'

    def activate(self, install_directory):
        return { 'PATH': '%s/bin' % install_directory }

    def available(self):
        base = os.getcwd()

        return {
                '1.0' : {
                    'url' : 'file://%s/testdata/makeapp/makeapp-1.0.tar.gz' %  base
                },
                '2.0' : {
                    'url' : 'file://%s/testdata/makeapp/makeapp-2.0.tar.gz' %  base
                },
                '3.0' : {
                    'url' : 'file://%s/testdata/makeapp/makeapp-3.0.tar.gz' %  base
                },
                '4.0' : {
                    'url' : 'http://badurl'
                }
         }

