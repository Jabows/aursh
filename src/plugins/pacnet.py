# -*- coding: utf-8 -*-

import os
import urllib
import json

from core.plugin import Plugin, plugin_command
from core import logger
from core import errors
from core.conf import configuration


_log = logger.get('pacnet')


class PacnetQuery(object):
    api_url = 'http://pacnet.karbownicki.com/api'
    search_modes = ['package', 'category']

    def __init__(self, search_mode='package', name=None):
        if search_mode not in self.search_modes:
            raise errors.BadUsage('Unknown pacnet query mode')
        self._query = {
            'base': self.api_url,
            'mode': search_mode,
            'filter': name,
        }

    @property
    def url(self):
        fl = self._query['filter']
        mode = self._query['mode']
        if mode == 'package':
            mode = 'packages'
            if fl:
                mode = 'search'
        elif mode == 'category' and not fl:
            mode = 'categories'
        q_path = [self._query['base'], mode]
        if fl:
            q_path.append(fl)
        query_url = '/'.join(q_path) + '/'
        _log.debug('query url: %s', query_url)
        return query_url


    def filter(self, name):
        self._query['filter'] = name

    def fetch(self):
        conn = urllib.urlopen(self.url)
        try:
            raw_result = conn.read()
        finally:
            conn.close()
        results = json.loads(raw_result)
        return results


class Pacnet(Plugin):
    """Pacnet CLI interface for aursh.
    Want to know what is pacnet? Visit http://pacnet.karbownicki.com/
    """

    @plugin_command('search', '[<package name>]')
    def search(self, pkg_name=None):
        """Search for given package in pacnet database.
        If no package name was given, return list of all packages.
        """
        q = PacnetQuery('package', pkg_name)
        results = q.fetch()
        for p in results:
            self._show_package_info(p)

    @plugin_command('category', '[<category name>]')
    def category(self, category_name=None):
        """Show list of categories, of if <category name> was given, show all
        packages from that category.
        """
        q = PacnetQuery('category', category_name)
        results = q.fetch()
        results = q.fetch()
        if category_name:
            for pkg in results:
                self._show_package_info(pkg)
        else:
            for category in results:
                self.io.put(category['fields']['name'])

    def _show_package_info(self, pkg):
        for field in configuration.PACNET_PKG_FORMAT:
            field_name = field.capitalize().replace('__', ' ')
            field_value = pkg.get(field, None)
            if field_value:
                self.io.put('%20s: %s' % (field_name, field_value))
        self.io.put()
