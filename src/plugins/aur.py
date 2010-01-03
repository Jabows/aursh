# -*- coding: utf-8 -*-

import os
import json
import urllib

from core.plugin import Plugin, plugin_command


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
        print query.fetch()
        # TODO - stdout

    @plugin_command('search')
    def search(self, pkg_name):
        """Search package in AUR"""
        query = AurQuery('search')
        query.filter(arg=pkg_name)
        print query.fetch()
        # TODO - stdout


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
        print os.path.join(self.aur_download_url, url_path)
        # TODO - download

    @plugin_command('upload')
    def upload(self, pkg_path):
        """Upload given package package"""
        raise NotImplemented

    @plugin_command('edit')
    def edit(self, pkg_name):
        """Download package from aur, run editor and push back"""
        raise NotImplemented

    def _extract_aur_package(self, package_path):
        raise NotImplemented

    def _run_package_build(self, package_dir):
        raise NotImplemented
