aursh configuration
===================

:Author: phusiatynski@gmail.com
:Date:   2010-01-03
:mod:`configuration` --- basic aursh configuration

overview
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


.. describe:: DEBUG
Set to  `True` to run aursh in debug mode.

.. describe:: LOGGING_DIRECTORY
Root directory for log files

.. describe:: LOGGING_LEVELS
Custom log levels 

.. describe:: LOGGING_CONFIGURATION
TODO

.. describe:: AUR_BUILD_DIRECTORY
Root directory for aursh builds

.. describe:: AUR_URL_MAIN
AUR main page url

.. describe:: AUR_URL_LOGIN
AUR user login link 

.. describe:: AUR_URL_SUBMIT
AUR user submit link

.. describe:: AUR_USERNAME
AUR user login

.. describe:: AUR_PASSWORD
AUR user password

.. describe:: MAKEPKG
Command for building package

.. describe:: PKG_INSTALL
Command for installink package

.. describe:: PKG_EXT
Arch Linux package extension

.. describe:: AUR_PKG_BUILD
AUR tarball creation command

.. describe:: AUR_PKG_EXT
AUR tarball extension

.. describe:: PKGBUILD_NAME
PKGBUILD` file name

.. describe:: EDITOR
Default editor

.. describe:: AUR_SEARCH_FORMAT
List of fields shown by `aur search` command

.. describe:: AUR_INFO_FORMAT
Cist of fields shown by `aur info` command
