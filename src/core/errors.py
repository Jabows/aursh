# -*- coding: utf-8 -*-


class AurshError(Exception):
    pass


class UnknownCommand(AurshError):
    pass


class BadUsage(AurshError):
    pass


class ConfigurationError(AurshError):
    pass


class PluginError(AurshError):
    pass
