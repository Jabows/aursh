aursh configuration
===================

:Author: phusiatynski@gmail.com
:Date:   2010-01-03
:mod:`configuration` --- basic aursh configuration

overwiev
--------

Configuration file can be placed in any file set with `$AURSHRC` envinonment
variable, in `$HOME/.aursh/aurshrc`, `$HOME/.config/aursh/aurshrc` or
`/usr/share/aursh/aurshrc`.

Configuration file is being loaded as Python module. You can write whatever
you want there, as lons as it's valid.

Instead of configuration file, you can set environment variable with `AURSH_`
prefix added to base variable name.


configuration variables
-----------------------

`ALIASSES` - By default, all commands are available using plugin name and
  that plugin command handler. But because you may wany to use `pacman`-like
  names, there's alias system.


`DEBUG` - set to  `True` to run aursh in debug mode.

`LOGGING_DIRECTORY` - root directory for log files

`LOGGING_LEVELS` - custom log levels 

`LOGGING_CONFIGURATION` - TODO

`AUR_BUILD_DIRECTORY` - rood directory for aursh builds

`AUR_URL_MAIN` - AUR main page url

`AUR_URL_LOGIN` - AUR user login link 

`AUR_URL_SUBMIT` - AUR user submit link

`AUR_USERNAME` - AUR user login

`AUR_PASSWORD` - AUR user password

`MAKEPKG` - command for building package

`PKG_INSTALL` - command for installink package

`PKG_EXT` - Arch Linux package extension

`AUR_PKG_BUILD` - AUR tarball creation command

`AUR_PKG_EXT` - AUR tarball extension

`PKGBUILD_NAME` - `PKGBUILD` file name

`EDITOR` - default editor

`AUR_SEARCH_FORMAT` - list of fields shown by `aur search` command

`AUR_INFO_FORMAT` - list of fields shown by `aur info` command
