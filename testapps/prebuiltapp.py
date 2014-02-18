
from ubrew.app import PreBuiltBinaryRecipe
import os


class PreBuiltAppRecipe(PreBuiltBinaryRecipe):
    
    name = 'prebuiltapp'

    def activate(self, install_directory):
        return { 'PATH': '%s/bin' % install_directory }

    def available(self):
        base = os.getcwd()

        return {
                '1.0' : {
                    'url' : 'file://%s/testdata/prebuiltapp/prebuiltapp-1.0.tgz' %  base
                },
                '2.0' : {
                    'url' : 'file://%s/testdata/prebuiltapp/prebuiltapp-2.0.tar.gz' %  base
                },
                '3.0' : {
                    'url' : 'file://%s/testdata/prebuiltapp/prebuiltapp-3.0.tar.gz' %  base
                },
                '4.0' : {
                    'url' : 'http://badurl'
                }
         }

