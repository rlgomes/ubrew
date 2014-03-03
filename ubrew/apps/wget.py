"""
"""

import urllib.request
import re
import os

from bs4 import BeautifulSoup

from ubrew.app import AutoconfRecipe


class WGetRecipe(AutoconfRecipe):

    __FTP_LOCATION='http://ftp.gnu.org/gnu/wget/'

    name = 'wget'

    def arguments(self):
        return [ ]

    def use(self, install_directory):
        return {
                'PATH' : '%s/bin' % install_directory
               }

    def available(self):
        htmldata = urllib.request.urlopen(WGetRecipe.__FTP_LOCATION).read()
        soup = BeautifulSoup(htmldata)

        def add_to(major, version):
            if major not in versions:
                versions[major] = []

            versions[major].append(version)

        # keep the order that is presented of the versions by mozilla
        versions = {}
        
        for link in soup.find_all('a'):
            href = link.get('href')
            
            match = re.match('wget\-([0-9\.]+)\.tar\.gz$', href)
            if match:
                version = match.group(1)
                url = '%s/%s' % (WGetRecipe.__FTP_LOCATION, href) 
                versions[version] = { 'url': url }

        return versions
    
    def install(self, download_directory, install_directory, arguments):
        # lets configure and install to the desired location
        os.chdir(download_directory)

        self.run('configure',
                 ['./configure', 
                  '--prefix=%s' % install_directory,
                  '--without-ssl'])
        self.run('build', ['make'])
        self.run('install', ['make','install'])

