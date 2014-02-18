"""
"""

__DESCRIPTION =  'ubrew easy installation and management of apps in user space'

import argparse

import re
import os
import sys
import shutil

from ubrew.util import retrieve, sort_versions, load_app_recipes
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


def clean(cache_directory):
    shutil.rmtree(cache_directory)
    os.mkdir(cache_directory)

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


def active(apps, install_directory):
    
    print('Active Applications:')
    for (app_name, app) in apps:
        app_directory = '%s/%s' % (install_directory, app_name)

        if os.path.exists(app_directory):
            versions = os.listdir(app_directory)
            if len(versions) != 0:
                for version in versions:
                    variables = app.use(version)
                    
                    active = True
                    for var in variables.keys():
                        lookup = variables[var]
                        if lookup not in os.environ[var]:
                            active = False

                    if active:
                        print(' * %s-%s is active' % (app_name, version))

    
def available(apps, unstable_releases=False):
    """
    """
    
    print('Installable Versions:')
    for (app_name, app) in apps:
        try:
            available = app.available()
            versions = available.keys()
            versions = sort_versions(versions)
                
            grouped_versions = {}
            print('\n%s:' % app_name)
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
            sys.exit(1)


def installed(apps, install_directory):

    print('Installed Versions:')
    for (app_name, app) in apps:
        app_directory = '%s/%s' % (install_directory, app_name)
        
        if os.path.exists(app_directory):
            versions = sort_versions(os.listdir(app_directory))
        else:
            versions = []

        if len(versions) != 0:
            print('%s:\n %s' % (app_name, ', '.join(versions)))
            print('')


def add_app_parsers(base_parser,
                    recipes,
                    with_arguments=False,
                    app_parser_required=True,
                    arguments=[(('version',), {'default': 'all'})]):
    # no we are going to find all of the available apps to install and populate
    # their names into the app choices as well as their sub arguments
    apps_parser = base_parser.add_subparsers(dest='app')
    apps_parser.required = app_parser_required

    for (app_name, app) in recipes:
        app_parser = apps_parser.add_parser(app_name)
        
        for (args, kwargs) in arguments:
            app_parser.add_argument(*args, **kwargs)

        if with_arguments:
            for argument in app.arguments():
                app_parser.add_argument(argument)


def main():
    recipes = load_app_recipes()

    parser = argparse.ArgumentParser(description=__DESCRIPTION)

    parser.add_argument('--version',
                        action='version',
                        version='ubrew %s' % __VERSION_STRING)

    subparsers = parser.add_subparsers(title='actions',
                                       dest='action',
                                       help='sub-command help')
    subparsers.required = True

    install_parser = subparsers.add_parser('install',
                                           help='install help')
    add_app_parsers(install_parser, recipes, with_arguments = True)

    uninstall_parser = subparsers.add_parser('uninstall',
                                             help='uninstall help')
    add_app_parsers(uninstall_parser, recipes, with_arguments = True)

    available_parser = subparsers.add_parser('available',
                                             help='available help')
    add_app_parsers(available_parser,
                    recipes,
                    app_parser_required=False,
                    arguments=[(('--unstable-releases',),
                                {'action':'store_true'})])

    use_parser = subparsers.add_parser('use',
                                       help='use help')
    add_app_parsers(use_parser, recipes)

    installed_parser = subparsers.add_parser('installed',
                                             help='installed help')
    add_app_parsers(installed_parser,
                    recipes,
                    app_parser_required=False,
                    arguments=[])

    active_parser = subparsers.add_parser('active',
                                          help='active help')
    add_app_parsers(active_parser,
                    recipes,
                    app_parser_required=False,
                    arguments=[])

    active_parser = subparsers.add_parser('clean',
                                          help='Erase downloaded archive files')
    
    args = parser.parse_args()
    install_directory, cache_directory = setup()
    
    if args.action == 'clean':
        return clean(cache_directory)
    
    if args.app == None:
        apps = recipes
        app_name = None
        app_version = None
    else:
        for (app_name, app) in recipes:
            if app_name == args.app:
                break

        app_version = ''
        try:
            app_version = args.version
        except:
            pass

        app_name = args.app
        apps = [(app_name, app)]

    if args.action == 'install':
        return install(app, app_name, app_version, install_directory, cache_directory)

    elif args.action == 'uninstall':
        return uninstall(app, app_name, app_version, install_directory)

    elif args.action == 'use':
        app_directory = '%s/%s' % (install_directory, app_name)
        final_directory = '%s/%s' % (app_directory, app_version)
        if os.path.exists(final_directory):
            variables = app.use(final_directory)
            for key in variables.keys():
                print('%s=%s' % (key, variables[key]))
        else:
            sys.stderr.write('%s-%s not installed.' % (app_name, app_version))
            sys.exit(1)

    elif args.action == 'active':
        return active(apps, install_directory)

    elif args.action == 'available':
        return available(apps, unstable_releases=False) #args.unstable_releases)

    elif args.action == 'installed':
        return installed(apps, install_directory)

    
    sys.exit(0)

if __name__ == '__main__':
    main()
