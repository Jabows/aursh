# -*- coding: utf-8 -*-


class AurshError(Exception):
    pass


class UnknownCommand(AurshError):
    pass


class UnknownPackage(AurshError):
    pass


class BadUsage(AurshError):
    pass


class ConfigurationError(AurshError):
    pass


class UnknownSetting(ConfigurationError):
    pass


class PluginError(AurshError):
    pass


class MissinFile(AurshError):
    pass


class PackageError(AurshError):
    submessage = 'Package error: %s'

    def __init__(self, pkg_name):
        self.pkg_name = pkg_name
        message = self.submessage % self.pkg_name
        super(PackageError, self).__init__(message)


class PackageNotFound(PackageError):
    submessage = 'Package not found: %s'


class PackageBuildError(PackageError):
    submessage = 'Can\'t build package: %s'


class PackageInstallationError(PackageError):
    submessage = 'Can\'t install package: %s'
