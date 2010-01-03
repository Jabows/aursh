aur --- AUR management plugin
=============================

:Author: phusiatynski@gmail.com
:Date:   2010-01-03

aur plugin commands handlers
----------------------------


`search <name>` - search in AUR for application with given name

`info <name>` - show info about package with given name

`download <name>` - download extract AUR tarball with given name

`make <name>` - build package from PKGBUILD

`upload [<name>|<package path>] <category>` - upload given AUR tarball

`edit <name> <category>` - download, extract, run editor, pack and upload
tarball with given name

`clean <name>` - clean given package build directory - remove all files

`vote <name>` - vote on package

`unvote <name>` - remove vote

`hash <name>` - show hash for given package (it does have to be downloaded
allready)
