# Copyright 2016 Isotoma Limited

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function

import contextlib
import os
import subprocess
import sys
from datetime import datetime

from flake8.hooks import git_hook as flake8_git_hook
from isort import SortImports
from isort.hooks import get_lines, get_output


def _datetime_token():
    return datetime.now().isoformat(' ')


@contextlib.contextmanager
def stash_unstaged(is_needed):
    """Tries to make a stash with a unique name.

    Then tries to re-apply this stash if it was successfully made.

    Becomes a pair of no-ops if is_needed is False.

    """

    class StashContext(object):
        success = True

    token = _datetime_token()
    message = 'Isort save - {}'.format(token)
    if is_needed:
        subprocess.check_call(['git', 'stash', 'save', '-k', message])

    ctx = StashContext()
    yield ctx

    if is_needed:
        # Check for a stash with the expected message.
        for line in get_lines('git stash list'):
            stash, stash_message = line.strip().split(': ', 1)
            if stash_message.endswith(message):
                stash_pop_return_code = subprocess.call(['git', 'stash', 'pop', stash])
                if stash_pop_return_code != 0:
                    ctx.success = False
                break
        else:
            print('No matching stash found.')


# Copy of git_hook from isort.hooks, but altered to force actual
# updating of the imports.
def isort_git_hook(strict=False, force=True):
    """
    Git pre-commit hook to check staged files for isort errors
    :param bool strict - if True, return number of errors on exit,
        causing the hook to fail. If False, return zero so it will
        just act as a warning.
    :return number of errors if in strict mode, 0 otherwise.
    """

    # Get list of files modified and staged
    diff_cmd = "git diff-index --cached --name-only --diff-filter=ACMRTUXB HEAD"
    python_files_modified = [filename for filename in get_lines(diff_cmd) if filename.endswith('.py')]

    errors = 0

    # If we're using force, then stash the unstaged changes. This
    # means we can just run isort and stage the results. Otherwise,
    # because we run isort and stage the whole file, the changes that
    # started of unstaged will become staged and committed.
    with stash_unstaged(is_needed=force) as stash_context:
        for filename in python_files_modified:
            if force:
                SortImports(filename)
                # Re-add the file
                subprocess.check_call(['git', 'add', filename])
            else:
                # Get the staged contents of the file
                staged_cmd = "git show :%s" % filename
                staged_contents = get_output(staged_cmd)

                sort = SortImports(
                    file_path=filename,
                    file_contents=staged_contents.decode(),
                    check=True
                )

                if sort.incorrectly_sorted:
                    errors += 1

    if not stash_context.success:
        # The stash was messy, but we should not error. We want the
        # commit to be complete. If we have left the current working
        # copy in a mess, then that's OK.
        print('### Error: stash did not pop cleanly ###')
        print('### Working copy may have unresolved merges ###')
    elif force:
        # Because of the stash-unstash, we will be left in a state of
        # unsorted imports, so sort them now, but only if the stash-pop
        # was ok, otherwise we'll just make things worse.
        for filename in python_files_modified:
            SortImports(filename)

    return errors if strict else 0


def _find_dir(name, start=None):
    if not start:
        start = os.getcwd()
    path = os.path.join(start, name)
    if os.path.isdir(path):
        return path
    parent = os.path.dirname(start)
    if start == parent:
        return None
    return _find_dir(name, parent)


def _find_node_modules_eslint():
    # Look for a local node_modules and use that
    node_modules = _find_dir('node_modules')
    if node_modules:
        possible_path = os.path.join(node_modules, '.bin', 'eslint')
        if os.path.isfile(possible_path):
            return possible_path


def eslint(path=None, strict=False):
    if not path:
        path = _find_node_modules_eslint()
        if not path:
            # Hope that it is installed globally.
            path = 'eslint'
    # Get list of files modified and staged
    diff_cmd = "git diff-index --cached --name-only --diff-filter=ACMRTUXB HEAD"
    js_files_modified = [filename for filename in get_lines(diff_cmd) if filename.endswith('.js')]
    if js_files_modified:
        errors = subprocess.call([path] + js_files_modified)
        return errors if strict else 0
    return 0


def kwargs_remove_prefix(kwargs, prefix):
    return {k[len(prefix):]: v for k, v in kwargs.items() if k.startswith(prefix)}


def hook(**kwargs):
    flake8_kwargs = kwargs_remove_prefix(kwargs, 'flake8_')
    isort_kwargs = kwargs_remove_prefix(kwargs, 'isort_')
    eslint_kwargs = kwargs_remove_prefix(kwargs, 'eslint_')
    sys.exit(
        isort_git_hook(**isort_kwargs) or
        flake8_git_hook(**flake8_kwargs) or
        eslint(**eslint_kwargs))
