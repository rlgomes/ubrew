"""
URL: https://github.com/LuaDist/lua
"""

import urllib.request
import re
import os
import platform
import shutil

from bs4 import BeautifulSoup

from ubrew.app import UBrewAppMakeBuild

def _get_platform():
    # aix ansi bsd generic linux macosx mingw posix solaris
    system_string = platform.system()

    if system_string == 'Linux':
        return 'linux'
    elif system_string == 'Darwin':
        return 'macosx'
    else:
        raise Exception('unsupported os platform %s' % system_string)


class UBrewApp(UBrewAppMakeBuild):

    __FTP_LOCATION='http://www.lua.org/ftp/'


    def arguments(self):
        return [ ]


    def use(self, install_directory):
        return {
                'PATH' : '%s/bin' % install_directory
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
        
        for link in soup.find_all('a'):
            href = link.get('href')

            if href:
                match = re.match('lua\-([0-9\.]+)\.tar\.gz$', href)
                if match:
                    version = match.group(1)
                    url = '%s/%s' % (UBrewApp.__FTP_LOCATION, href) 
                    versions[version] = { 'url': url }

        return versions

    def install(self, download_directory, install_directory):
        os.chdir(download_directory)
        
        version = 0.0
        if os.path.exists('%s/include/lua.h' % download_directory):
            lines = open('%s/include/lua.h' % download_directory) .read()
            for line in lines.split('\n'):
                match = re.match('#define.*LUA_VERSION.*"Lua ([0-9]+\.[0-9]+).*"', line)
                if match:
                    version = float(match.group(1))
                    break
        elif os.path.exists('%s/src/lua.h' % download_directory):
            # newer lua.h location after 5.1 
            lines = open('%s/src/lua.h' % download_directory) .read()
            for line in lines.split('\n'):
                match = re.match('#define LUA_VERSION_MAJOR.*"([0-9]+)"', line)
                if match:
                    version = float(match.group(1))

                match = re.match('#define LUA_VERSION_MIN.*"([0-9]+)"', line)
                if match:
                    version += float('0.' + match.group(1))

                match = re.match('#define.*LUA_VERSION.*"Lua ([0-9]+\.[0-9]+).*"', line)
                if match:
                    version = float(match.group(1))
        else:
            # version less than 3.0
            version = 1.0
        print('Detected lua version %s' % version)
        
        if version < 2.0:
            if os.system('make') != 0:
                print('Failed to build lua, please see log for details')
        if version < 3.0:
            if os.path.exists('%s/domake' % download_directory):
                if os.system('./domake') != 0:
                    print('Failed to build lua, please see log for details')
            else:
                print('Failed to build lua, expected domake script.')
        elif version >= 3.0 and version < 5.0:
            config = open('%s/config' % download_directory, 'r') .read()
            config = config.replace('INSTALL_ROOT= /usr/local',
                           'INSTALL_ROOT= %s' % install_directory)

            output = open('%s/config' % download_directory, 'w')
            output.write(config)
            output.close()
        
            if os.system('make') != 0:
                print('Failed to build application, please see log for details')
            
            if version < 4.0:
                shutil.copytree('%s/bin' % download_directory, '%s/bin' % install_directory)
                shutil.copytree('%s/lib' % download_directory, '%s/lib' % install_directory)
                shutil.copytree('%s/include' % download_directory, '%s/include' % install_directory)
            else:
                if os.system('make install') != 0:
                    print('Failed to install application, please see log for details')
        else:
            if version < 5.1:
                config = open('%s/config' % download_directory, 'r') .read()
                config = config.replace('INSTALL_ROOT= /usr/local',
                            'INSTALL_ROOT= %s' % install_directory)

                output = open('%s/config' % download_directory, 'w')
                output.write(config)
                output.close()
            else:
                config = open('%s/Makefile' % download_directory, 'r') .read()
                config = config.replace('INSTALL_TOP= /usr/local',
                            'INSTALL_TOP= %s' % install_directory)

                output = open('%s/Makefile' % download_directory, 'w')
                output.write(config)
                output.close()
 
            if os.system('make %s' % _get_platform())  != 0:
                print('Failed to build lua, please see log for details')

            if os.system('make install') != 0:
                if os.path.exists(install_directory):
                    shutil.rmtree(install_directory)
                print('Failed to install application, please see log for details')

