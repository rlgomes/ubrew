"""
"""

import platform
import urllib.request
import re

from bs4 import BeautifulSoup

from ubrew.app import UBrewAppMakeBuild

class UBrewApp(UBrewAppMakeBuild):

    __FTP_LOCATION='http://www.python.org/ftp/python/'


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
               ]

    def use(self, install_directory):
        return {
                'PATH' : '%s/bin' %install_directory
               }

    def available(self):
        htmldata = urllib.request.urlopen(UBrewApp.__FTP_LOCATION).read()
        soup = BeautifulSoup(htmldata)

        def add_to(major, version):
            if major not in versions:
                versions[major] = []

            versions[major].append(version)

        # keep the order that is presented of the versions by mozilla
        versions = {}
        
        for tr in soup.find_all('tr'):
            tds = tr.find_all('td')
            if tds:
                try:
                    version = tds[1].a.get_text()[0:-1]
                    
                    if re.match('[0-9]+.*', version):
                        ext = self._get_platform_extension()
                        url = '%s/%s/Python-%s%s' % (UBrewApp.__FTP_LOCATION, version, version, ext)

                        versions[version] = { 'url': url }
                except:
                    pass

        return versions

