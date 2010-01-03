# -*- coding: utf-8 -*-

import os
import json
import urllib
import urllib2
import cookielib
import shutil
import tarfile
import subprocess
import hashlib

from libs.multipartposthandler import MultipartPostHandler

from core.plugin import Plugin, plugin_command
from core.conf import configuration
from core.io import IO
from core import logger
from core import errors


_log = logger.get('aur')


class AurQuery(object):
    aur_rpc_url = 'http://aur.archlinux.org/rpc.php'
    allowed_queries = set(['info', 'search'])

    def __init__(self, query_type):
        assert query_type in self.allowed_queries
        self._query_params = {'type': query_type}

    @property
    def query_type(self):
        return self._query_params['type']

    def filter(self, **kwds):
        self._query_params.update(kwds)
        return self

    def _params(self):
        return urllib.urlencode(self._query_params)

    def _to_url(self):
        return self.aur_rpc_url + '?' + self._params()

    def fetch(self):
        conn = urllib.urlopen(self._to_url())
        try:
            raw_result = conn.read()
        finally:
            conn.close()
        return json.loads(raw_result)


class AurAuth(object):
    """All actions that require AUR registration"""

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
    aur_download_url = 'http://aur.archlinux.org/'
    aur_package_url = 'http://aur.archlinux.org/packages.php?ID=%d'
    allowed_categories = (None, 'daemons', 'devel', 'editors', 'emulators',
            'games', 'gnome', 'i18n', 'kde', 'kernels', 'lib', 'modules',
            'multimedia', 'network', 'office', 'science', 'system', 'x11',
            'xfce')

    io = IO()

    @plugin_command('info')
    def info(self, pkg_name):
        """Get info about given package"""
        query = AurQuery('info')
        query.filter(arg=pkg_name)
        result = query.fetch()
        self._show_aur_info_result(result)

    @plugin_command('search')
    def search(self, pkg_name):
        """Search package in AUR"""
        query = AurQuery('search')
        query.filter(arg=pkg_name)
        result = query.fetch()
        self._show_aur_search_result(result)

    @plugin_command('pkgbuild')
    def pkgbuild(self, pkg_name):
        pass

    @plugin_command('download')
    def download(self, pkg_name):
        """Download package from AUR"""
        query = AurQuery('info')
        pkg = query.filter(arg=pkg_name).fetch()
        if pkg['type'] == 'error':
            # TODO - does not exist
            return
        url_path = pkg['results']['URLPath']
        if url_path.startswith('/'):
            url_path = url_path[1:]
        pkg_aur_url = os.path.join(self.aur_download_url, url_path)
        pkg_aur_name = pkg_aur_url.rsplit('/', 1)[1]
        pkg_dest = os.path.join(
                self._create_package_directory(pkg_name), pkg_aur_name)
        _log.debug('fetching package from: %s', pkg_aur_url)
        _log.debug('pkg_dest: %s', pkg_dest)
        urllib.urlretrieve(pkg_aur_url, pkg_dest)
        self._extract_package(pkg_name, pkg_dest)
        return True

    @plugin_command('make')
    def make(self, pkg_name, *flags):
        return self._run_package_build(pkg_name, flags)

    @plugin_command('upload')
    def upload(self, pkg, category):
        """Upload given package package"""
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
        aur_auth(configuration.AUR_URL_SUBMIT, form_data)
        return True

    @plugin_command('edit')
    def edit(self, pkg_name, category):
        """Download package from aur, run editor and push back"""
        self.download(pkg_name)
        self._edit_pkgbuild(pkg_name)
        self.upload(pkg_name, category)

    @plugin_command('clean')
    def clean(self, pkg_name):
        self._remove_package_directory(pkg_name)

    @plugin_command('install')
    def intsall(self, pkg_name):
        self.download(pkg_name)
        self.make(pkg_name)
        self._run_package_install(pkg_name)

    @plugin_command('comment')
    def comment(self, pkg_name, *message):
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

    @plugin_command('vote')
    def vote(self, pkg_name, vote_type=None):
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

    @plugin_command('hash')
    def hash(self, pkg_name):
        for tarball in self._find_aur_tarballs(pkg_name):
            pkg_hash = self._get_tarball_md5(tarball)
            pkg_name = tarball.rsplit('/', 1)[1]
            self.io.put('%42s: %s' % (pkg_name, pkg_hash))
        return True

    @plugin_command('unvote')
    def unvote(self, pkg_name):
        return self.vote(pkg_name, 'unvote')

    def _extract_package(self, pkg_name, archive_path):
        archive = tarfile.open(archive_path, 'r:gz')
        archive.extractall(self._get_package_directory(pkg_name))

    def _create_package_directory(self, pkg_name):
        path = self._get_package_directory(pkg_name)
        if not os.path.isdir(path):
            os.makedirs(path)
        else:
            _log.debug('package directory allready exists: %s', path)
        return path

    def _remove_package_directory(self, pkg_name):
        path = self._get_package_directory(pkg_name)
        if not os.path.isdir(path):
            return False
        shutil.rmtree(path)
        return True

    def _get_package_directory(self, pkg_name):
        return os.path.join(configuration.AUR_BUILD_DIRECTORY, pkg_name)

    def _run_package_build(self, pkg_name, makepkg_flags):
        chdir_to = os.path.join(
                self._get_package_directory(pkg_name), pkg_name)
        _log.debug('changing working directory to: %s', chdir_to)
        os.chdir(chdir_to)
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
                install_proc = subprocess.Popen(install_cmd, shell=True)
                exit_status = os.waitpid(install_proc.pid, 0)
                if exit_status[1] != 0:
                    raise errors.PackageInstall(pkg_name)
        raise errors.PackageNotFound

    def _show_aur_search_result(self, data):
        show_format = configuration.AUR_SEARCH_FORMAT
        if data['type'] == 'error':
            _log.debug('bad search result: %s', data)
            self.io.put(data['results'])
            return
        for result in data['results']:
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
