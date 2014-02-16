"""
"""

import platform
import urllib.request
import re
import os

from bs4 import BeautifulSoup

from ubrew.app import UBrewAppMakeBuild

class UBrewApp(UBrewAppMakeBuild):

    __FTP_LOCATION='http://ftp.vim.org/pub/vim/'


    def _get_platform(self):
        system_string = platform.system()

        if system_string == 'Linux':
            return 'unix'
        elif system_string == 'Darwin':
            return 'mac'
        else:
            raise Exception('unsupported os platform %s' % system_string)

    def arguments(self):
        return [ ]

    def use(self, install_directory):
        return { 
                'PATH' : '%s/bin' % install_directory
               }

    def available(self):
        platform = self._get_platform()
        baseurl = '%s/%s' % (UBrewApp.__FTP_LOCATION, platform)
        htmldata = urllib.request.urlopen(baseurl).read()
        soup = BeautifulSoup(htmldata)

        # keep the order that is presented of the versions by mozilla
        versions = {}
        
        for link in soup.find_all('a'):
            try:
                filename = link.get_text()
                match = re.match('vim\-([0-9\.]+)\.tar\.(gz|bz2)$', filename)
                if match:
                    version = match.group(1)
                    url = '%s/%s' % (baseurl, filename)
                    versions[version] = { 'url': url } 

            except:
                pass

        return versions

    def install(self, download_directory, install_directory):
        os.chdir(download_directory)
        
        version = 0.0
        version_file = '%s/src/version.c' % download_directory
        if os.path.exists(version_file):
            if os.path.exists(version_file):
                lines = open(version_file) .read()
                for line in lines.split('\n'):
                    match = re.match('char.*\*Version = "VIM ([0-9\.]+)";', line)
                    if match:
                        version = float(match.group(1))
                        break

                    match = re.match('char.*\*Version = "([0-9\.]+)";', line)
                    if match:
                        version = float(match.group(1))
                        break

        version_file = '%s/src/version.h' % download_directory
        if os.path.exists(version_file):
            if os.path.exists(version_file):
                lines = open(version_file) .read()
                for line in lines.split('\n'):
                    match = re.match('#define.*VIM_VERSION_MEDIUM.*"([0-9\.]+)"', line)
                    if match:
                        version = float(match.group(1))
                        break

        
        if version >= 3.0 and version <= 4.0:
            raise Exception('Building any 3.0 builds is not supported at this time')
        elif version >= 5.0 and version < 6.0:
            raise Exception('Building any 5.0 builds is not supported at this time')
        elif version >= 4.0:
            os.chdir('%s/src' % download_directory)
            
            self.run('configure', ['./configure','--prefix=%s' % install_directory])
            self.run('build', ['make'])
            self.run('install', ['make','install'])
        else:
            raise Exception('unsupported version %s' % version)


