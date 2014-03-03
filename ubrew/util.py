
import urllib.request
from urllib.parse import urlparse

import sys
import shutil
import tarfile
import os

import inspect
import pkgutil
import importlib

from ubrew.app import AppRecipe

def retrieve(fromurl, cache_directory, outdirectory):
    url = urlparse(fromurl)

    if url.scheme == 'git' or 'github' in url.path:
        if '#tag' in fromurl:
            # checkout from git and the version should be marked using #tag=xxx
            url, tag = fromurl.split('#')
            tag = tag.split('=')[1]

            os.chdir(outdirectory)
            os.system('git clone %s .' % url)
            os.system('git checkout tags/%s' % tag)
        else:
            # not tag means we're just cloning the base repository
            os.chdir(outdirectory)
            os.system('git clone %s .' % fromurl)

    elif url.scheme == 'http' or url.scheme == 'https':
        outfilename = '%s/%s' % (cache_directory, os.path.basename(fromurl))

        def chunk_report(bytes_so_far, chunk_size, total_size):
            percent = float(bytes_so_far) / total_size
            percent = round(percent*100, 2)
            sys.stdout.write("%d of %d bytes (%0.2f%%)\r" % 
                (bytes_so_far, total_size, percent))

            if bytes_so_far >= total_size:
                sys.stdout.write('\n')

        def chunk_read(response, output, chunk_size=1024*16, report_hook=None):
            total_size = response.getheader('Content-Length').strip()
            total_size = int(total_size)
            bytes_so_far = 0

            while 1:
                chunk = response.read(chunk_size)
                output.write(chunk)
                bytes_so_far += len(chunk)

                if not chunk:
                    break

                if report_hook:
                    report_hook(bytes_so_far, chunk_size, total_size)
            
            return bytes_so_far

        # if it was already downloaded then lets not waste time
        if not os.path.exists(outfilename):
            # download to a different file name because if we fail in the middle then
            # we won't have "comitted" the download
            tmpoutfilename = '%s.download' % outfilename
            outputfile = open(tmpoutfilename, 'wb')
            print('Downloading %s' % fromurl)
            response = urllib.request.urlopen(fromurl)
            chunk_read(response, outputfile, report_hook=chunk_report)
            outputfile.close()
            
            # we've downloaded the file so lets "commit" it over to the desired name
            # and we now know we have the complete file
            shutil.move(tmpoutfilename, outfilename)
        else:
            print('Already downloaded %s' % fromurl)

        print('Extracting tarball to %s' % outdirectory)
        tar = tarfile.open(outfilename)
        tar.extractall(outdirectory)
        tar.close()

        files = os.listdir(outdirectory)
        if len(files) == 1:
            # uncompressed to output directory but ended up with another directory 
            # inside of this one, so lets move that back one level
            basepath = '%s/%s' % (outdirectory, files[0])
            tmppath = basepath + '_tmp'
            shutil.move(basepath, tmppath)
            subfiles = os.listdir(tmppath)
            for path in subfiles:
                shutil.move('%s/%s' % (tmppath, path), outdirectory)
            
    elif url.scheme == 'file':
        # just retrieve it from the specified file location
        outfilename = '%s/%s' % (cache_directory, os.path.basename(fromurl))
        shutil.copy(url.path, outfilename)

        print('Extracting tarball to %s' % outdirectory)
        tar = tarfile.open(outfilename)
        tar.extractall(outdirectory)
        tar.close()

        files = os.listdir(outdirectory)
        if len(files) == 1:
            basepath = '%s/%s' % (outdirectory, files[0])
            subfiles = os.listdir(basepath)
            for path in subfiles:
                shutil.move('%s/%s' % (basepath, path), outdirectory)

    else:
        raise Exception('unsupported protocol %s' % url.scheme)

import re
from distutils.version import Version

class LooseVersion (Version):
    """
    Taken from distutils and adapted to work better when comparing verisons that
    don't follow the same structure such as 1.0.3 and 1.0-a
    """

    component_re = re.compile(r'(\d+ | [a-z]+ | \.)', re.VERBOSE)

    def __init__ (self, vstring=None):
        if vstring:
            self.parse(vstring)


    def parse (self, vstring):
        # I've given up on thinking I can reconstruct the version string
        # from the parsed tuple -- so I just store the string here for
        # use by __str__
        self.vstring = vstring
        components = [x for x in self.component_re.split(vstring)
                              if x and x != '.']
        for i, obj in enumerate(components):
            try:
                components[i] = int(obj)
            except ValueError:
                pass

        self.version = components


    def __str__ (self):
        return self.vstring


    def __repr__ (self):
        return "LooseVersion ('%s')" % str(self)


    def _cmp (self, other):
        if isinstance(other, str):
            other = LooseVersion(other)

        if len(self.version) < len(other.version):
            shortest = len(self.version)
        else:
            shortest = len(other.version)

        for index in range(0, shortest):
            self_component = self.version[index]
            other_component = other.version[index]

            if type(self_component) != type(other_component):
                self_component = str(self_component)
                other_component = str(other_component)

            if self_component == other_component:
                continue

            if self_component < other_component:
                return -1

            if self_component > other_component:
                return 1

        return len(self.version) - len(other.version)        

def sort_versions(versions):
    return sorted(versions, key = LooseVersion) 

if os.environ.get('UBREW_PACKAGES', None):
    __APP_PKGS = ['ubrew.apps'] + os.environ.get('UBREW_PACKAGES').split(',')
else:
    __APP_PKGS = ['ubrew.apps']

def load_app_recipes():
    recipes = []

    for package in __APP_PKGS:
        package_module = importlib.import_module(package)
        package_path = os.path.dirname(package_module.__file__)

        for (_, module, _) in pkgutil.iter_modules([package_path]):
            try:
                if module == 'app':
                    continue

                ubrew_module = importlib.import_module('%s.%s' % (package, module)) 

                for member in dir(ubrew_module):
                    member_value = getattr(ubrew_module, member)

                    if not hasattr(member_value, 'name'):
                        continue

                    if inspect.isclass(member_value):
                        app = member_value()
                        if issubclass(app.__class__, AppRecipe):
                            app_name = getattr(app, 'name')
                            recipes.append((app_name, app))
            except:
                import traceback
                traceback.print_exc()
                pass

    return sorted(recipes)

