"""
define the interface for any ubrew app
"""

import shutil
import os
import subprocess
import tempfile
from ubrew import log


class AppRecipe(object):


    def arguments(self):
        """
        return a list of keyword arguments that the command line tool can expose
        to the end user and which will be passed as key word arguments to the 
        install method. These arguments in the form --with-special get 
        translated into keyword arguments and passed to the install function, 
        like the following examples:

            --with-special => with_special=True
            --optimize=3 => optimize=3

        """
        return []

    def available(self):
        """
        returns a dictionary of the versions available and at least the url for
        each of those versions where we can download the tar ball, like so:

            {
                1.0 : {
                    url : 'http://xxx/blah-1.0.tar.gz'
                },
                2.0 : {
                    url : 'http://xxx/blah-1.0.tar.gz'
                },
                2.1 : {
                    url : 'http://xxx/blah-1.0.tar.gz'
                },
                ...
            }
        """
        raise Exception('implement me')


    def use(self, install_directory):
        """
        return the name of the environment variables you'd like to prepend 
        entries to. usually you just want to prepend to the existing PATH but 
        in the case of things like python you'd want to prepend to the 
        PYTHONTPATH as well.
        """
        return { 'PATH': install_directory }


    def install(self, download_directory, install_directory, arguments):
        """
        you can override this method to take introduce any special installation
        steps that are necessary to install the ubrew application to the 
        install_directory specified and the uncompressed contents of the current
        version are in the download_directory specified.
        """
        pass


    def info(self, stepname, message):
        log.info('%s: %s' % (stepname, message))


    def warn(self, stepname, message):
        log.warn('%s: %s' % (stepname, message))


    def error(self, stepname, message):
        log.error(' %s: %s' % (stepname, message))


    def run(self, stepname, args):
        """
        runs the command specified in the args argument
        """
        self.info(stepname, 'Running [%s]' % ' '.join(args))
        tempdir = tempfile.mktemp()
        os.makedirs(tempdir)
        logfile = '%s/%s.log' % (tempdir, stepname)
        log = open(logfile, 'w')
        
        status = subprocess.call(args, stdout=log, stderr=log)
        if status != 0:
            self.error(stepname, 'check %s for details.' % logfile)
            raise Exception('Failed to run [%s]' % ' '.join(args))


class PreBuiltBinaryRecipe(AppRecipe):
    """
    pre built binary package only needs to be moved to its new location be 
    installed
    """

    def install(self, download_directory, install_directory, arguments):
        # prebuilt and we can just copy it over
        shutil.move(download_directory, install_directory)


class AutoconfRecipe(AppRecipe):
    """
    The simplest autoconf project requires a ./configure with the --prefix 
    assigned to the installation directory and a simple 'make' followed by a 
    'make install' to get everything built and installed correctly.
    """

    def install(self, download_directory, install_directory, arguments):
        # lets configure and install to the desired location
        os.chdir(download_directory)

        self.run('configure', ['./configure', '--prefix=%s' % install_directory])
        self.run('build', ['make'])
        self.run('install', ['make','install'])


class GitSourceRecipe(AppRecipe):
    """
    """

    def __init__(self, source):
        self.source = source

    def available(self):
        """
        all available versions are the exact tag names that the git repo has.
        """
        tags = {}

        process = subprocess.Popen(['git', 'ls-remote', '--tags', self.source],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        
        output, _ = process.communicate()

        if process.wait() != 0:
            raise Exception('unable to retrieve tags for %s' % self.source)

        lines = output.decode('utf-8').split('\n')

        for line in lines:
            if line.strip() != '':
                tag = line.split('/')[2]
                tags[tag] = { 'url' : '%s#tag=%s' % (self.source, tag) }

        return tags


class SetuptoolsRecipe(AppRecipe):
    """
    recipe for installing and enabling a python setuptools package.
    """

    def _which_python(self):
        """
        based on the PYTHONPATH variable we can figure out the exact python 
        version that is installed.
        """
        pythonpath = os.environ['PYTHONPATH']
        splits = pythonpath.split(':')
        pythonpath = os.path.abspath(splits[-1])

        for path in os.listdir(pythonpath):
            if 'python' in path:
                return path

        raise Exception('unable to determine which python version is in use') 

    def use(self, install_directory):
        """
        return the name of the environment variables you'd like to prepend 
        entries to. usually you just want to prepend to the existing PATH but 
        in the case of things like python you'd want to prepend to the 
        PYTHONTPATH as well.
        """
        return {
                'PATH': '%s/bin' % install_directory,
                'PYTHONPATH': '%s/lib/%s/site-packages' %
                              (install_directory, self._which_python()),
               }


    def install(self, download_directory, install_directory, arguments):

        os.chdir(download_directory) 
        self.run('build',['python', 'setup.py', 'build'])
        
        # you can only install to a custom location if that location has the
        # directory /lib/pythonX.Y/site-packages in the PYTHONPATH
        python = self._which_python()
        ppath = '%s/lib/%s/site-packages' % (install_directory, python)
        os.makedirs(ppath)
        original_python_path = os.environ['PYTHONPATH']
        try:
            os.environ['PYTHONPATH'] = '%s:%s' % (ppath, os.environ['PYTHONPATH'])
            self.run('install',['python', 'setup.py', 'install', '--prefix=' + install_directory])
        finally:
            os.environ['PYTHONPATH'] = original_python_path
        

