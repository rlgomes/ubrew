"""
"""

__DESCRIPTION =  'ubrew easy installation and management of apps in user space'

import argparse
import importlib

import re
import os
import sys
import shutil
import pkgutil

from ubrew.util import retrieve, sort_versions
from ubrew import log

from ubrew.version import __VERSION_STRING


def setup():
    base_directory = '%s/.ubrew' % os.path.expanduser('~') 

    install_directory = '%s/apps' % base_directory
    cache_directory = '%s/cache' % base_directory

    if not os.path.exists(base_directory):
        os.mkdir(base_directory)

    if not os.path.exists(install_directory):
        os.mkdir(install_directory)

    if not os.path.exists(cache_directory):
        os.mkdir(cache_directory)
    
    return install_directory, cache_directory


def __install(app, app_name, app_version, install_directory, cache_directory, download_url):
    log.info('installing %s-%s' % (app_name, app_version))
    app_directory = '%s/%s' % (install_directory, app_name)
    if not os.path.exists(app_directory):
        os.makedirs(app_directory)

    final_directory = '%s/%s' % (app_directory, app_version)

    if os.path.exists(final_directory):
        raise Exception('%s-%s already installed' % (app_name, app_version))

    out_directory = '%s/%s' % (cache_directory, app_name)
    if os.path.exists(out_directory):
        shutil.rmtree(out_directory)
    os.makedirs(out_directory)

    retrieve(download_url, cache_directory, out_directory)

    final_directory = '%s/%s' % (app_directory, app_version)
    app.install(out_directory, final_directory)


def install(app, app_name, app_version, install_directory, cache_directory):
    available = app.available()
    versions = available.keys()
    versions = sort_versions(versions)

    if app_version == 'all':
        failed = False
        # lets attempt to install every available version
        for version in versions:
            download_url = available[version]['url']
            try:
                __install(app, app_name, version, install_directory, cache_directory, download_url)
            except Exception as e:
                failed = True
                log.error(str(e))
                pass

        if failed:
            sys.exit(1)

    elif app_version in versions:
        download_url = available[app_version]['url']
        __install(app, app_name, app_version, install_directory, cache_directory, download_url)
    else:
        print('version %s is unavailable.' % app_version)
        sys.exit(1)


def uninstall(app, app_name, app_version, install_directory):
    app_directory = '%s/%s' % (install_directory, app_name)
    final_directory = '%s/%s' % (app_directory, app_version)
    if os.path.exists(final_directory):
        shutil.rmtree(final_directory)
    else:
        print('%s-%s is not installed.' % (app_name, app_version))
        sys.exit(1)


def active(app, app_name, install_directory):
    app_directory = '%s/%s' % (install_directory, app_name)

    if os.path.exists(app_directory):
        versions = os.listdir(app_directory)
        if len(versions) != 0:
            for version in versions:
                variables = app.activate(version)
                
                active = True
                for var in variables.keys():
                    lookup = variables[var]
                    if lookup not in os.environ[var]:
                        active = False

                if active:
                    print(' %s-%s is active' % (app_name, version))
                    return

    print(' %s no active version' % app_name) 
    sys.exit(1)

    
def available(app, app_name, app_version, unstable_releases=False):
    """
    """
    try:
        print('Installable Versions')
        available = app.available()
        versions = available.keys()
        versions = sort_versions(versions)
            
        grouped_versions = {}
        for version in versions:
            if unstable_releases:
                match = re.match('([a-z0-9]+\.[a-z0-9]+).*', version)
            else:
                match = re.match('([a-z0-9]+\.[a-z0-9]+)\.?[a-z0-9]*$', version)

            if match:
                major = match.group(1)
                if major not in grouped_versions:
                    grouped_versions[major] = []

                grouped_versions[major].append(version)

        majors = grouped_versions.keys()
        majors = sort_versions(majors)
        for major in majors:
            sub_versions = grouped_versions[major]
            print(' * %s' % ' '.join(sub_versions))

    except:
        import traceback
        traceback.print_exc()
        print('unable to find the app with specified signature %s-%s' % 
                        (app_name, app_version))
        sys.exit(1)


def installed(app, app_name, install_directory):
    app_directory = '%s/%s' % (install_directory, app_name)
    
    if os.path.exists(app_directory):
        versions = os.listdir(app_directory)
        if len(versions) != 0:
            print('Installed Versions')
            versions = sort_versions(versions)
            for version in versions:
                print(' * %s' % version)

            return

    print('%s is not installed.' % app_name)
    sys.exit(1)

if os.environ.get('UBREW_PACKAGES', None):
    __APP_PKGS = ['ubrew.apps'] + os.environ.get('UBREW_PACKAGES').split(',')
else:
    __APP_PKGS = ['ubrew.apps']

def add_app_parsers(base_parser,
                    with_arguments=False,
                    arguments=[(('version',),{})]):
    # no we are going to find all of the available apps to install and populate
    # their names into the app choices as well as their sub arguments
    apps_parser = base_parser.add_subparsers(dest='app')
    apps_parser.required = True
    
    for package in __APP_PKGS:
        package_module = importlib.import_module(package)
        package_path = os.path.dirname(package_module.__file__)

        for (_, module, _) in pkgutil.iter_modules([package_path]):
            try:
                if module == 'app':
                    continue

                ubrew_module = importlib.import_module('%s.%s' % (package, module)) 
                app = ubrew_module.UBrewApp()

                app_parser = apps_parser.add_parser(module)
 
                for (args,kwargs) in arguments:
                    app_parser.add_argument(*args, **kwargs)

                if with_arguments:
                    for argument in app.arguments():
                        app_parser.add_argument(argument)
            except:
                import traceback
                traceback.print_exc()
                pass


def main():
    parser = argparse.ArgumentParser(description=__DESCRIPTION)

    parser.add_argument('--version',
                        action='version',
                        version='ubrew %s' % __VERSION_STRING)

    subparsers = parser.add_subparsers(dest='action', help='sub-command help')
    subparsers.required = True

    install_parser = subparsers.add_parser('install', help='install help')
    add_app_parsers(install_parser, with_arguments = True)

    uninstall_parser = subparsers.add_parser('uninstall', help='uninstall help')
    add_app_parsers(uninstall_parser, with_arguments = True)

    available_parser = subparsers.add_parser('available', help='available help')
    add_app_parsers(available_parser,
                    arguments=[(('--unstable-releases',),
                                {'action':'store_true'})])

    installed_parser = subparsers.add_parser('installed', help='installed help')
    add_app_parsers(installed_parser, arguments=[])

    activate_parser = subparsers.add_parser('activate', help='activate help')
    add_app_parsers(activate_parser)

    deactivate_parser = subparsers.add_parser('deactivate', help='deactivate help')
    add_app_parsers(deactivate_parser)

    active_parser = subparsers.add_parser('active', help='active help')
    add_app_parsers(active_parser, arguments=[])

    active_parser = subparsers.add_parser('cleanup', help='clean up cache')
    add_app_parsers(active_parser, arguments=[])
    
    args = parser.parse_args()
    brew_app = None

    for package_path in __APP_PKGS:
        package_name = package_path.replace('/','.')
        try:
            brew_app = importlib.import_module('%s.%s' % (package_name, args.app))
        except:
            pass

    if not brew_app:
        print('application %s not found.' % args.app)
        return -1

    app = brew_app.UBrewApp()
    install_directory, cache_directory = setup()

    app_version = ''
    try:
        app_version = args.version
    except:
        pass

    app_name = args.app

    if args.action == 'install':
        return install(app, app_name, app_version, install_directory, cache_directory)

    elif args.action == 'uninstall':
        return uninstall(app, app_name, app_version, install_directory)

    elif args.action == 'active':
        return active(app, app_name, install_directory)

    elif args.action == 'activate':
        app_directory = '%s/%s' % (install_directory, app_name)
        final_directory = '%s/%s' % (app_directory, app_version)
        if os.path.exists(final_directory):
            variables = app.activate(final_directory)
            for key in variables.keys():
                print('%s=%s' % (key, variables[key]))
        else:
            sys.stderr.write('%s-%s not installed.' % (app_name, app_version))
            sys.exit(1)

    elif args.action == 'deactivate':
        app_directory = '%s/%s' % (install_directory, app_name)
        final_directory = '%s/%s' % (app_directory, app_version)
        if os.path.exists(final_directory):
            variables = app.activate(final_directory)
            for key in variables.keys():
                print('%s=%s' % (key, variables[key]))
        else:
            sys.stderr.write('%s-%s not installed.' % (app_name, app_version))
            sys.exit(1)

    elif args.action == 'available':
        return available(app,
                         app_name,
                         app_version,
                         unstable_releases=args.unstable_releases)

    elif args.action == 'installed':
        return installed(app, app_name, install_directory)
    
    sys.exit(0)

if __name__ == '__main__':
    main()
