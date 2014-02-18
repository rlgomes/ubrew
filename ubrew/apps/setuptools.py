"""
"""

import urllib.request
import re

from bs4 import BeautifulSoup

from ubrew.app import SetuptoolsRecipe


class SetuptoolsRecipe(SetuptoolsRecipe):

    __FTP_LOCATION='https://pypi.python.org/packages/source/s/setuptools/'
    
    name = 'setuptools'

    def arguments(self):
        return [
                '--with-pydebug',
               ]

    def use(self, install_directory):
        return {
                'PATH' : '%s/bin' %install_directory
               }

    def available(self):
        htmldata = urllib.request.urlopen(SetuptoolsRecipe.__FTP_LOCATION).read()
        soup = BeautifulSoup(htmldata)

        def add_to(major, version):
            if major not in versions:
                versions[major] = []

            versions[major].append(version)

        # keep the order that is presented of the versions by mozilla
        versions = {}
        
        for link in soup.find_all('a'):
            try:
                name = link.get_text()
                match = re.match('setuptools-([0-9a-z\.]+).tar.gz', name)
                
                if match:
                    version = match.group(1)
                    url = '%s/%s' % (SetuptoolsRecipe.__FTP_LOCATION, name)
                    versions[version] = { 'url': url }
            except:
                pass

        return versions

