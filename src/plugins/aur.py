# -*- coding: utf-8 -*-

import os
import re
import json
import urllib
import urllib2
import cookielib
import shutil
import tarfile
import subprocess
import hashlib

from libs.multipartposthandler import MultipartPostHandler
from libs.pkgbuild import Pkgbuild

from core.plugin import Plugin, plugin_command
from core.conf import configuration
from core import logger
from core import errors
from core.tools import compare_versions


_log = logger.get('aur')


class AurQuery(object):
    """AUR query creator.


    Class created to simplify AUR json api access.
    """

    aur_rpc_url = 'http://aur.archlinux.org/rpc.php'
    allowed_queries = set(['info', 'search'])

    def __init__(self, query_type):
        assert query_type in self.allowed_queries
        self._query_params = {'type': query_type}

    @property
    def query_type(self):
        "Get current query object type"
        return self._query_params['type']

    def filter(self, **kwds):
        "Filter using given parameters"
        self._query_params.update(kwds)
        return self

    def _params(self):
        return urllib.urlencode(self._query_params)

    def _to_url(self):
        "Convert all given filter parameters to url"
        return self.aur_rpc_url + '?' + self._params()

    def fetch(self):
        "Fetch objects from AUR, using given filters"
        conn = urllib.urlopen(self._to_url())
        try:
            raw_result = conn.read()
        finally:
            conn.close()
        return json.loads(raw_result)


class AurAuth(object):
    """AUR web page authentication.

    All actions that require AUR account.
    """

    def __init__(self, login, password):
        self.login = login
        self.password = password

    def __call__(self, *args, **kwds):
        if not hasattr(self, '_opener'):
            self._auth()
        return self._opener.open(*args, **kwds)

    def _auth(self):
        """Create authorized opener"""
        cookiejar = cookielib.CookieJar()
        auth_data = urllib.urlencode(
                dict(user=self.login, passwd=self.password, name='0'))
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar),
                MultipartPostHandler)
        request = urllib2.Request(configuration.AUR_URL_LOGIN, auth_data)
        opener.open(request)
        self._opener = opener
        return self


class Aur(Plugin):
    """AUR management helper plugin
    """
    aur_download_url = 'http://aur.archlinux.org/'
    aur_package_url = 'http://aur.archlinux.org/packages.php?ID=%d'
    allowed_categories = (None, 'daemons', 'devel', 'editors', 'emulators',
            'games', 'gnome', 'i18n', 'kde', 'kernels', 'lib', 'modules',
            'multimedia', 'network', 'office', 'science', 'system', 'x11',
            'xfce')


    @plugin_command('info', '<package name>')
    def info(self, pkg_name):
        "Get info about given package"
        query = AurQuery('info')
        query.filter(arg=pkg_name)
        result = query.fetch()
        self._show_aur_info_result(result)

    @plugin_command('search', '<search term>')
    def search(self, pkg_name):
        "Search package in AUR"
        rx = None
        # basic regexp support for search results
        if pkg_name.startswith('^'):
            pkg_name = pkg_name[1:]
            rx = re.compile(pkg_name)
        if pkg_name.endswith('$'):
            if rx is None:
                rx = re.compile(pkg_name)
            pkg_name = pkg_name[:-1]
        if not pkg_name:
            raise errors.BadUsage('Search string is empty')
        query = AurQuery('search')
        query.filter(arg=pkg_name)
        result = query.fetch()
        self._show_aur_search_result(result, rx)

    @plugin_command('pkgbuild', '<package name>')
    def pkgbuild(self, pkg_name):
        "Read PKGBUILD form AUR and show selected values"
        pkgbuild = self._fetch_pkgbuild(pkg_name)
        pkg_data = pkgbuild.parseall()
        for field in configuration.PKGBUILD_FORMAT:
            data = pkg_data.get(field, None)
            if not data:
                continue
            if isinstance(data, list) or isinstance(data, tuple):
                data = ', '.join(data)
            data = data.decode('utf-8')
            data = data.strip()
            field = field.capitalize()
            self.io.put("%s: %s" % (field.rjust(16), data))
        return True

    @plugin_command('download', '<package name>')
    def download(self, pkg_name):
        "Download package from AUR"
        query = AurQuery('info')
        pkg = query.filter(arg=pkg_name).fetch()
        if pkg['type'] == 'error':
            raise errors.PackageNotFound(pkg_name)
        url_path = pkg['results']['URLPath']
        if url_path.startswith('/'):
            url_path = url_path[1:]
        pkg_aur_url = os.path.join(self.aur_download_url, url_path)
        pkg_aur_name = pkg_aur_url.rsplit('/', 1)[1]
        pkg_dest = os.path.join(
                self._create_package_directory(pkg_name), pkg_aur_name)
        _log.debug('fetching package from: %s', pkg_aur_url)
        _log.debug('pkg_dest: %s', pkg_dest)
        self.io.info('downloading package: %s' % pkg_aur_url)
        urllib.urlretrieve(pkg_aur_url, pkg_dest)
        self._extract_tarball(pkg_name, pkg_dest)
        return True

    @plugin_command('make', '<package name>')
    def make(self, pkg_name, *flags):
        "Build package."
        return self._run_package_build(pkg_name, flags)

    @plugin_command('upload', '<package name> <AUR category>')
    def upload(self, pkg, category):
        "Upload given package tarball"
        if not category in self.allowed_categories:
            raise errors.BadUsage('Unknown category: %s' % category)
        if os.path.isdir(pkg):
            pkg = self._build_aur_package(directory=pkg)
        elif not os.path.isfile(pkg):
            pkg = self._build_aur_package(pkg_name=pkg)
        aur_auth = AurAuth(configuration.AUR_USERNAME,
                configuration.AUR_PASSWORD)
        _log.debug('uploading package: %s (%s)', pkg, category)
        form_data = {
            'pkgsubmit': '1',
            'category': self.allowed_categories.index(category),
            'pfile': open(pkg, 'rb'),
        }
        self.io.info('uploading package: %s' % pkg)
        aur_auth(configuration.AUR_URL_SUBMIT, form_data)
        return True

    @plugin_command('edit', '<package name> <AUR category>')
    def edit(self, pkg_name, category):
        "Download package from aur, run editor and push back"
        self.download(pkg_name)
        self._edit_pkgbuild(pkg_name)
        self.upload(pkg_name, category)

    @plugin_command('clean', '<package name>')
    def clean(self, pkg_name):
        "Clean package build directory"
        self._remove_package_directory(pkg_name)

    @plugin_command('install', '<package name>, [<package name>, ...]')
    def install(self, *packages):
        "Download, build and install package"
        for pkg_name in packages:
            self.download(pkg_name)
            self.make(pkg_name)
            self._run_package_install(pkg_name)

    @plugin_command('comment', '<package name> <message>')
    def comment(self, pkg_name, *message):
        "Add comment on given package AUR web page"
        message = ' '.join(message)
        package_id = self._get_package_id(pkg_name)
        aur_auth = AurAuth(configuration.AUR_USERNAME,
                configuration.AUR_PASSWORD)
        form_data = {
            'comment': message,
            'ID': package_id,
        }
        comment_url = self.aur_package_url % package_id
        aur_auth(comment_url, form_data)
        return True

    @plugin_command('vote', '<package name>')
    def vote(self, pkg_name, vote_type=None):
        "Vote on package"
        vote = {'do_Vote': True}
        if vote_type in ['down', '-', '-1', 'remove', 'unvote']:
            vote = {'do_UnVote': 'UnVote'}
        package_id = self._get_package_id(pkg_name)
        vote_url = self.aur_package_url % package_id
        aur_auth = AurAuth(configuration.AUR_USERNAME,
                configuration.AUR_PASSWORD)
        form_data = {
            'ID': package_id,
        }
        form_data['IDs[%d]' % package_id] = 1
        form_data.update(vote)
        x = aur_auth(vote_url, form_data)
        return True

    @plugin_command('hash', '<package name>')
    def hash(self, pkg_name):
        "Print hashes for all packages in given package name build directory"
        for tarball in self._find_aur_tarballs(pkg_name):
            pkg_hash = self._get_tarball_md5(tarball)
            pkg_name = tarball.rsplit('/', 1)[1]
            self.io.put('%42s: %s' % (pkg_name, pkg_hash))
        return True

    @plugin_command('unvote', '<package name>')
    def unvote(self, pkg_name):
        "Remove vote for given package"
        return self.vote(pkg_name, 'unvote')

    @plugin_command('upgrade')
    def upgrade(self):
        "Upgrade all package installed from AUR"
        to_upgrade = {}
        for (pkg_name, version) in self._get_all_aur_packages():
            new_version = self._is_package_outdated(pkg_name, version)
            if not new_version:
                continue
            to_upgrade[pkg_name] = (version, new_version)
        if not to_upgrade:
            self.io.info('Everything is up to date')
            return True
        self.io.info('Following packages will be upgraded from AUR:')
        for (pkg_name, versions) in to_upgrade.iteritems():
            self.io.put('  %26s  %8s -> %s' % \
                    (pkg_name, versions[0], versions[1]))
        self.io.info('Continue?  [y/N]: ', newline=False)
        response = self.io.read_char()
        if response not in 'yY':
            raise errors.QuitSilently
        for pkg_name in to_upgrade:
            self.install(pkg_name)
        return True

    def _find_missing_dependencies(self, pkg_name):
        raise NotImplemented

    def _is_package_outdated(self, pkg_name, version):
        """Check in AUR if package with given name and version is outdated.

        Returns False or new version.
        """
        query = AurQuery('info')
        query.filter(arg=pkg_name)
        result = query.fetch()
        if result['type'] == 'error':
            _log.debug('bad search result: %s', pkg_name)
            self.io.warning('package does not exist in AUR: %s' % pkg_name)
            return
        pkg = result['results']
        assert pkg_name == pkg['Name']
        aur_version = pkg['Version']
        try:
            if compare_versions(version, aur_version) < 0:
                return aur_version
        except TypeError:
            self.io.warning('can\'t compare versions: %s - %s' % \
                    (version, aur_version))
        return False

    def _get_all_aur_packages(self):
        """Get list of packages installed from AUR

        Return format is (package name, package version), both string type.
        """
        aur_pkg_cmd = configuration.AUR_INSTALLED_PKG.split()
        aur_pkg_lister = subprocess.Popen(aur_pkg_cmd, stdout=subprocess.PIPE)
        exit_status = os.waitpid(aur_pkg_lister.pid, 0)
        for pkg_info in aur_pkg_lister.stdout:
            yield pkg_info.split()

    def _extract_tarball(self, pkg_name, archive_path):
        "Extract given package tarball"
        archive = tarfile.open(archive_path, 'r:gz')
        archive.extractall(self._get_package_directory(pkg_name))

    def _create_package_directory(self, pkg_name, *args):
        """Create package build directory based on it's name and optional
        arguments.
        """
        path = self._get_package_directory(pkg_name)
        path = os.path.join(path, *args)
        if not os.path.isdir(path):
            os.makedirs(path)
        else:
            _log.debug('package directory allready exists: %s', path)
        return path

    def _remove_package_directory(self, pkg_name):
        "Clean tarball build directory by removing it"
        path = self._get_package_directory(pkg_name)
        if not os.path.isdir(path):
            return False
        self.io.info('removing directory: %s' % path)
        shutil.rmtree(path)
        return True

    def _get_package_directory(self, pkg_name, *args):
        "Remove package build directory path"
        return os.path.join(configuration.AUR_BUILD_DIRECTORY, pkg_name, *args)

    def _run_package_build(self, pkg_name, makepkg_flags):
        chdir_to = self._get_package_directory(pkg_name, pkg_name)
        if not os.path.isdir(chdir_to):
            raise errors.PackageNotFound(pkg_name)
        _log.debug('changing working directory to: %s', chdir_to)
        os.chdir(chdir_to)
        pkgbuild = Pkgbuild('PKGBUILD')
        deps_groups = self._check_deps(pkgbuild.parse_depends())
        if deps_groups['missing']:
            raise errors.PackageNotFound('Can\'t find packages: %s' % \
                    ', '.join(deps_groups['missing']))
        if deps_groups['repo']:
            self.io.info('Following packages will be installed from repository:')
            for dep in deps_groups['repo']:
                self.io.put('\t%s' % dep)
        if deps_groups['aur']:
            self.io.info('Following packages will be installed from AUR:')
            for dep in deps_groups['aur']:
                self.io.put('\t%s' % dep)
            self.io.info('Continue?  [y/N]: ', newline=False)
            response = self.io.read_char()
            self.io.put()
            if response not in 'Yy':
                raise errors.QuitSilently
        for aur_dep in deps_groups['aur']:
            self.install(aur_dep)
        makepkg_cmd = configuration.MAKEPKG + ' ' + ' '.join(makepkg_flags)
        makepkg = subprocess.Popen(makepkg_cmd, shell=True)
        exit_status = os.waitpid(makepkg.pid, 0)
        if exit_status[1] != 0:
            raise errors.PackageBuildError(pkg_name)
        return True

    def _run_package_install(self, pkg_name):
        chdir_to = os.path.join(
                self._get_package_directory(pkg_name), pkg_name)
        _log.debug('changing working directory to: %s', chdir_to)
        os.chdir(chdir_to)
        for f in os.listdir(chdir_to):
            if f.endswith(configuration.PKG_EXT):
                install_cmd = configuration.PKG_INSTALL + ' ' + f
                _log.debug('running package installer: %s', install_cmd)
                exit_status = subprocess.call(install_cmd)
                _log.debug('installation ended with: %d', exit_status)
                if exit_status:
                    raise errors.PackageInstallationError(pkg_name)
                return
        _log.debug('didn\'t found any package in: %s', chdir_to)
        raise errors.PackageNotFound

    def _show_aur_search_result(self, data, rx_name=None):
        show_format = configuration.AUR_SEARCH_FORMAT
        if data['type'] == 'error':
            _log.debug('bad search result: %s', data)
            self.io.put(data['results'])
            return
        for result in data['results']:
            if rx_name:
                for field_name in ['Name', 'Description']:
                    value = result.get(field_name, '')
                    if rx_name.search(value):
                        break
                else:
                    continue
            for field_name in show_format:
                field_data = result.get(field_name)
                self.io.put('%20s: %s' % (field_name, field_data))
            self.io.put('')

    def _show_aur_info_result(self, data):
        show_format = configuration.AUR_INFO_FORMAT
        if data['type'] == 'error':
            _log.debug('bad search result: %s', data)
            self.io.put(data['results'])
            return
        result = data['results']
        for field_name in show_format:
            field_data = result.get(field_name)
            self.io.put('%20s: %s' % (field_name, field_data))

    def _build_aur_package(self, pkg_name=None, directory=None):
        def _find_or_build_package(pkg_directory):
            for root, dirs, files in os.walk(pkg_directory):
                if configuration.PKGBUILD_NAME in files:
                    os.chdir(root)
                    _log.debug('creating package in: %s', root)
                    build_cmd = configuration.AUR_PKG_BUILD
                    build_proc = subprocess.Popen(build_cmd, shell=True)
                    exit_status = os.waitpid(build_proc.pid, 0)
                    if exit_status[1] != 0:
                        raise errors.PackageBuildError(
                                'Can\'t build package: %s', pkg_name)
                    files = os.listdir(root)
                for f in files:
                    if f.endswith(configuration.AUR_PKG_EXT):
                        pkg_file = os.path.join(root, f)
                        _log.debug('found package for upload: %s', pkg_file)
                        return pkg_file
            return None
        if pkg_name and not directory:
            directory = self._get_package_directory(pkg_name)
        pkg_file = _find_or_build_package(directory)
        if pkg_file is None:
            raise errors.PackageBuildError(
                    'Can\'t find package for upload: %s' % pkg_name)
        _log.debug('package ready for upload: %s', pkg_file)
        return pkg_file

    def _edit_pkgbuild(self, pkg_name):
        pkgbuild = self._find_pkgbuild(pkg_name)
        if pkgbuild is None:
            raise errors.MissingFile('%s not found: %s',
                    configuration.PKGBUILD_NAME, pkg_name)
        exit_code = subprocess.call([configuration.EDITOR, pkgbuild])
        return True

    def _find_pkgbuild(self, pkg_name=None, directory=None):
        "Find PKGBUILD and retun full path to it or `None` if does not exist"
        assert pkg_name or directory
        if directory is None:
            directory = self._get_package_directory(pkg_name)
        for root, dirs, files in os.walk(directory):
            if configuration.PKGBUILD_NAME in files:
                return os.path.join(root, configuration.PKGBUILD_NAME)
        # if not found...
        return None

    def _find_aur_package(self, pkg_name):
        directory = os.path.join(
                self._get_package_directory(pkg_name), pkg_name)
        for root, dirs, files in os.walk(directory):
            for f in files:
                if f.endswith(configuration.AUR_PKG_EXT):
                    pkg_path = os.path.join(root, f)
                    return pkg_path
        return None

    def _get_package_id(self, pkg_name):
        query = AurQuery('info')
        query.filter(arg=pkg_name)
        result = query.fetch()
        if result['type'] == 'errors':
            raise errors.UnknownPackage('package not found: %s' % pkg_name)
        return int(result['results']['ID'])

    def _find_aur_tarballs(self, pkg_name):
        directory = os.path.join(
                self._get_package_directory(pkg_name), pkg_name)
        for root, dirs, files in os.walk(directory):
            for f in files:
                if f.endswith(configuration.AUR_PKG_EXT):
                    pkg_path = os.path.join(root, f)
                    yield pkg_path

    def _get_tarball_md5(self, pkg_path):
        with open(pkg_path) as pkg:
            return hashlib.md5(pkg.read()).hexdigest()

    def _fetch_pkgbuild(self, pkg_name):
        "Download PKGBUILD file from AUR and return `Pkgbuild` object"
        url = configuration.AUR_PACKAGES
        url = os.path.join(url, pkg_name, pkg_name,
                configuration.PKGBUILD_NAME)
        self.io.info('reading PKGBUILD: %s' % url)
        pkg_www = urllib.urlopen(url)
        if pkg_www.code != 200:
            raise errors.PkgbuildNotFound('Response code: %s' % pkg_www.code)
        pkgbuild = Pkgbuild(pkgbuild_text=pkg_www.read())
        return pkgbuild

    def _check_deps(self, deps_to_check):
        """Check each given package if it can be installed from arch
        repositore, AUR or it can't be installed.
        Returns dict with list of packages:
        {
            'repo': [...]
            'aur': [...]
            'missing': [...]
        }
        """
        cmd = ['pacman', '-T']
        cmd.extend(deps_to_check)
        deps_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        deps = deps_proc.stdout.read().split()
        if deps:
            self.io.info('missing dependencies:\n\t%s' % '\n\t'.join(deps))
        pacman_deps = []
        aur_deps = []
        missing_deps = []
        for dep in deps:
            if '>=' in dep:
                dep = dep.split('>=')[0]
            elif '<=' in dep:
                dep = dep.split('<=')[0]
            _log.debug('checking if packgage is in repo: %s', dep)
            pacman_retcode = subprocess.call(['pacman', '-Si', dep],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if pacman_retcode == 0:
                pacman_deps.append(dep)
                continue
            # check if it exists in AUR
            query = AurQuery('info')
            query.filter(arg=dep)
            result = query.fetch()
            if result['type'] == 'error':
                missing_deps.append(dep)
                continue
            aur_deps.append(dep)
        status = {
            'repo': pacman_deps,
            'aur': aur_deps,
            'missing': missing_deps,
        }
        _log.debug('package groups: %s', status)
        return status
