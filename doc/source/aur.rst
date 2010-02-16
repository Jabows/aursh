aur --- AUR management plugin
=============================

:Author: phusiatynski@gmail.com
:Date:   2010-01-03



aur plugin commands handlers
----------------------------


.. describe:: search <name>
Search in AUR for application with given name. You can use
`^` and `$` regular expression syntax symbols.

.. describe:: info <name>
Show info about package with given name

.. describe:: download <name>
Download extract AUR tarball with given name

.. describe:: make <name>
Build package from PKGBUILD

.. describe:: upload [<name>|<package path>] <category>
Upload given AUR tarball

.. describe:: edit <name> <category>
Download, extract, run editor, pack and upload tarball with given name

.. describe:: clean <name>
Clean given package build directory - remove all files

.. describe:: vote <name>
Vote on package

.. describe:: unvote <name>
Remove vote

.. describe:: hash <name>
Show hash for given package (it does have to be downloaded allready)



aur usage example
-----------------

This is quick example of how to use aursh to search & install package from
AUR.

First, search for package to see if it's in AUR::

    # aursh Ss aursh
            Name: aurshell-git
     Description: Shell for Arch Linux AUR management - currently under rewrite
         Version: 20100103-1

            Name: aursh-git
     Description: yet another AUR manager
         Version: 2-3


As you can see, instead od `aur search` you can just type `Ss`. This is an
allias, which can be changed in configuration file.

`Ss` option is using AUR json API, so it does not contain all informations.
But you may use `Si` (or `aur info`) which is parsing PKGBUILD file, to get
all data possible::

    # aursh Si aursh-git
    ==> reading PKGBUILD: http://aur.archlinux.org/packages/aursh-git/aursh-git/PKGBUILD
             Pkgname: aursh-git
         Contributor: Piotr Husiatyński <phusiatynski@gmail.com>
              Pkgrel: 3
              Pkgver: 2
             Pkgdesc: yet another AUR manager
                Arch: i686, x86_64
             License: GPL
             Depends: python>=2.6
         Makedepends: git
            Replaces: aurshell-git

Installation is also very simple::

    # aursh S aursh-git
    ==> downloading package: http://aur.archlinux.org/packages/aursh-git/aursh-git.tar.gz
    ==> Determining latest git revision...
      -> Version found: 20100216
    ==> Making package: aursh-git 20100216-1 i686 (Tue Feb 16 20:53:32 CET 2010)
    ==> Checking Runtime Dependencies...
    ==> Checking Buildtime Dependencies...
    ==> Retrieving Sources...
    ==> Extracting Sources...
    ==> Removing existing pkg/ directory...
    ==> Entering fakeroot environment...
    ==> Starting build()...
    ==> Connecting to git://github.com/husio/aursh.git git server
    Already up-to-date.
    ==> The local copy is up to date.
    ==> git checkout done
    ==> Starting make...
    ==> Tidying install...
      -> Stripping debugging symbols from binaries and libraries...
    ==> Creating package...
      -> Generating .PKGINFO file...
      -> Compressing package...
    bsdtar: Failed to set default locale
    ==> Leaving fakeroot environment.
    ==> Finished making: aursh-git 20100216-1 i686 (Tue Feb 16 20:53:33 CET 2010)
    loading package data...
    checking dependencies...
    (1/1) checking for file conflicts                   [##############################################] 100%
    (1/1) upgrading aursh-git                           [##############################################] 100%

and done.
