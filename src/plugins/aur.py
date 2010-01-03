# -*- coding: utf-8 -*-

import os
import json
import urllib
import shutil
import tarfile
import subprocess

from core.plugin import Plugin, plugin_command
from core.conf import configuration
from core import logger


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



class Aur(Plugin):
    aur_download_url = 'http://aur.archlinux.org/'

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
        with open(pkg_dest, 'w') as pkg:
            _log.debug('fetching package from: %s', pkg_aur_url)
            pkg_remote = urllib.urlopen(pkg_aur_url)
            pkg.write(pkg_remote.read())
            pkg_remote.close()
        _log.debug('pkg_dest: %s', pkg_dest)
        self._extract_package(pkg_name, pkg_dest)
        return True

    @plugin_command('make')
    def make(self, pkg_name, *flags):
        return self._run_package_build(pkg_name, flags)

    @plugin_command('upload')
    def upload(self, pkg_path):
        """Upload given package package"""
        raise NotImplemented

    @plugin_command('edit')
    def edit(self, pkg_name):
        """Download package from aur, run editor and push back"""
        raise NotImplemented

    @plugin_command('clean')
    def clean(self, pkg_name):
        self._remove_package_directory(pkg_name)

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

    def _show_aur_search_result(self, data):
        show_format = configuration.AUR_SEARCH_FORMAT
        if data['type'] == 'error':
            _log.debug('bad search result: %s', data)
            print data['results']
            return
        for result in data['results']:
            for field_name in show_format:
                field_data = result.get(field_name)
                print '%20s: %s' % (field_name, field_data)
            print ''

    def _show_aur_info_result(self, data):
        show_format = configuration.AUR_INFO_FORMAT
        if data['type'] == 'error':
            _log.debug('bad search result: %s', data)
            print data['results']
            return
        result = data['results']
        for field_name in show_format:
            field_data = result.get(field_name)
            print '%20s: %s' % (field_name, field_data)
