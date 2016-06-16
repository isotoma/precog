# precog
For preventing your crimes, before you can commit them.

Installation
============

To install from PyPI, run `pip install precog`. To install the
githook, run `precog`. This will try to write to your pre-commit file
(`.git/hooks/pre-commit`), and will abort if it already exists, so
move or remove it if you want to use precog.

Usage
=====

Once you have precog installed, your commits will be checked that they
conform. By default it will abort a commit if any of `flake8`, `isort`
or `eslint` do not exit cleanly, but will make no effort to fix any
problems. The pre-commit file contains the default values for the
options, but you can override the behaviour with environment variables
when committing, or if you can edit the defaults in the pre-commit file.

Examples:
---------

To skip all checking altogether, eg for a work-in-progress commit:
```
STRICT="" git commit -m "wip"
```
this will still print issues, but will let the commit complete.

To skip just isort:
```
ISORT_STRICT="" git commit -m "wip - todo: fix imports"
```

The `ISORT_FORCE` option
========================

This one is a bit mad. Because `isort` knows how to fix the problems
it finds (while `flake8` and `eslint` do not), rather than complaining
at you, this option tells `precog` to tweak your changed files to
conform to the `isort` checking. Though this is a bit scary, so is
disabled by default.

In the case where all of a file is staged for commit, this is fairly
straight-forward: `precog` will just run `isort` on the file and then
re-add it to include those changes in the commit. But if only part of
file is staged, then we don't want to add the whole file. So we make
use of the `-k` option to `git stash` to stash only the unstaged
changes. We then run `isort`, add the file, then pop the stash.

There are almost certainly edge-cases in this, and if it mucks up your
commit, then I am sorry. Out of your sadness, a PR/issue can rise to
make it not happen again.
