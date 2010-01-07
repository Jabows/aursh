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
