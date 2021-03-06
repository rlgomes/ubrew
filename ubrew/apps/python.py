"""
"""

import platform
import urllib.request
import os
import re

from bs4 import BeautifulSoup

from ubrew.app import AutoconfRecipe
from ubrew.util import retrieve

class PythonRecipe(AutoconfRecipe):

    __FTP_LOCATION='http://www.python.org/ftp/python/'

    name = 'python'

    def _get_platform_extension(self):
        system_string = platform.system()

        if system_string == 'Linux':
            return '.tgz'
        elif system_string == 'Darwin':
            return '-macosx10.3.dmg'
        else:
            raise Exception('unsupported os platform %s' % system_string)

    def arguments(self):
        return [
                '--with-pydebug',
                '--with-setuptools',
               ]

    def use(self, install_directory):
        return {
                'PATH' : '%s/bin' %install_directory
               }

    def available(self):
        htmldata = urllib.request.urlopen(PythonRecipe.__FTP_LOCATION).read()
        soup = BeautifulSoup(htmldata)

        def add_to(major, version):
            if major not in versions:
                versions[major] = []

            versions[major].append(version)

        # keep the order that is presented of the versions by mozilla
        versions = {}
        
        for a in soup.find_all('a'):
            try:
                version = a.get_text()[0:-1]
                
                if re.match('[0-9]+.*', version):
                    ext = self._get_platform_extension()
                    url = '%s/%s/Python-%s%s' % \
                            (PythonRecipe.__FTP_LOCATION, version, version, ext)

                    versions[version] = { 'url': url }
            except:
                pass

        return versions
    
    def install(self, download_directory, install_directory, arguments):
        AutoconfRecipe.install(self, download_directory, install_directory, arguments)
        
        # shall we install setuptools ? 
        if arguments.with_setuptools:
            fromurl = "https://pypi.python.org/packages/source/s/setuptools/setuptools-2.1.tar.gz"
            output_directory = '%s/setuptools' % download_directory
            retrieve(fromurl, download_directory, output_directory)

            os.chdir(output_directory)
            self.run('install', ['%s/bin/python' % install_directory,
                                 'setup.py',
                                 'install'])


