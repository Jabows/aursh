aursh installation
==================


:Author: phusiatynski@gmail.com
:Date:   2010-01-03
:mod:`installation` --- aursh installation instructions


using PKGBUILD
--------------

Just type in console::

    $ mkdir -p /tmp/aursh-git
    $ cd /tmp/aursh-git

    $ wget http://aur.archlinux.org/packages/aursh-git/aursh-git.tar.gz
    $ tar -xvvf aursh-git.tar.gz

    $ cd aursh-git
    $ makepkg

    $ sudo pacman -U aursh*


installation from source
------------------------

TODO, but here's the repo: http://github.com/husio/aursh/tree/v2
