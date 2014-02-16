"""
Firefox Browser
URL: https://ftp.mozilla.org/pub/mozilla.org/firefox/releases
"""

import locale
import platform
import urllib.request

import re
import os

from bs4 import BeautifulSoup
from ubrew.app import UBrewAppPreBuiltBinary


class UBrewApp(UBrewAppPreBuiltBinary):


    def _get_platform_string(self, ):
        system_string = platform.system()

        if system_string == 'Linux':
            if platform.architecture()[0] == '64bit':
                return 'linux-x86_64'
            else:
                return 'linux-i686'
        elif system_string == 'Darwin':
            return 'mac'
        else:
            raise Exception('unsupported os platform %s' % system_string)


    def _get_locale_string(self, ):
        locale.setlocale(locale.LC_ALL, '')
        return locale.getlocale()[0].replace('_','-')


    def __create_base_directory(self, base):
        base_directory = '%s/firefox' % base

        if not os.path.exists(base_directory):
            os.mkdir(base_directory)

        return base_directory 


    def use(self, install_directory):
        return {
                'PATH' : install_directory
               }


    def available(self):
        base  = 'https://ftp.mozilla.org/pub/mozilla.org/firefox/releases'
        htmldata = urllib.request.urlopen(base).read()
        soup = BeautifulSoup(htmldata)

        # keep the order that is presented of the versions by mozilla
        versions = {}
        
        for row in soup.find_all('tr'):
            columns = row.find_all('td')
            if columns:
                version = str(columns[1].a.get_text()[0:-1])

                if re.match('[0-9]+\..*', version):
                    lang = self._get_locale_string()
                    plat = self._get_platform_string()
                    filename = 'firefox-%s.tar.bz2' % version
                    url = '%s/%s/%s/%s/%s' % (base, version, plat, lang, filename)

                    versions[version] = {
                                        'url': url
                                            }

        return versions

