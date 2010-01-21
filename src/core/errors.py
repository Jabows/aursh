# -*- coding: utf-8 -*-


class AurshError(Exception):
    pass


class QuitSilently(Exception):
    pass


class Forbidden(AurshError):
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


class PkgbuildNotFound(MissinFile):
    pass


class PackageError(AurshError):
    pass


class PackageNotFound(PackageError):
    pass


class PackageBuildError(PackageError):
    pass


class PackageInstallationError(PackageError):
    pass
