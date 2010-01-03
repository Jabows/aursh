# -*- coding: utf-8 -*-

import os
import sys

from core.errors import ConfigurationError



class Configuration(dict):
    _conf_file = 'aursh/conf'

    def __init__(self):
        super(Configuration, self).__init__()
        self._load_configuration()

    def _configuration_file_path(self):
        # ~/.conf/<name>
        conf = os.path.join(os.getenv('HOME'), '.config', self._conf_file)
        if os.path.isfile(conf):
            return conf
        # ~/.<name>
        conf = os.path.join(os.getenv('HOME'), '.' +self._conf_file)
        if os.path.isfile(conf):
            return conf
        conf = os.path.join('/usr/share', self._conf_file)
        if os.path.isfile(conf):
            return conf
        raise ConfigurationError('Can\'t find configuration file')

    def _load_configuration(self):
        conf_file = self._configuration_file_path()
        conf_file_path, conf_file_name = conf_file.rsplit('/', 1)
        remove_conf_file_path = False
        if not conf_file_path in sys.path:
            sys.path.append(conf_file_path)
            remove_conf_file_path = True
        try:
            conf = __import__(conf_file_name)
            # cleanup in PYTHONPATH
            if remove_conf_file_path:
                sys.path.remove(conf_file_path)
        except ImportError as e:
            raise ConfigurationError(
                    'Configuration file contains erorrs'
                    '\n'.join(e.args))
        # update current object with data from configuration file
        for name in dir(conf):
            if not name.startswith('_'):
                self[name] = getattr(conf, name)
