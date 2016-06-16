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

import os
import stat
import sys

from flake8 import hooks


git_hook_file = '''#!/usr/bin/env python
import os
import precog


# The default for all the other *_STRICT values
STRICT = os.getenv('STRICT', True)

FLAKE8_COMPLEXITY = os.getenv('FLAKE8_COMPLEXITY', -1)
FLAKE8_STRICT = os.getenv('FLAKE8_STRICT', STRICT)
FLAKE8_IGNORE = os.getenv('FLAKE8_IGNORE')
FLAKE8_LAZY = os.getenv('FLAKE8_LAZY', False)
ISORT_STRICT = os.getenv('ISORT_STRICT', STRICT)
ISORT_FORCE = os.getenv('ISORT_FORCE', False)  # should isort rewrite your commit to fix it
ESLINT_STRICT = os.getenv('ESLINT_STRICT', STRICT)
ESLINT_PATH = os.getenv('ESLINT_PATH')  # path to the eslint executable


if __name__ == '__main__':
    precog.hook(
        flake8_complexity=FLAKE8_COMPLEXITY,
        flake8_strict=FLAKE8_STRICT,
        flake8_ignore=FLAKE8_IGNORE,
        flake8_lazy=FLAKE8_LAZY,
        isort_strict=ISORT_STRICT,
        isort_force=ISORT_FORCE,
        eslint_strict=ESLINT_STRICT,
        eslint_path=ESLINT_PATH)
'''


def install_git_hook():
    pre_commit_hook_path = hooks.find_vcs()
    if os.path.exists(pre_commit_hook_path):
        sys.exit('Error: hook already exists ({})'.format(pre_commit_hook_path))
    with open(pre_commit_hook_path, 'w') as fd:
        fd.write(git_hook_file)
    os.chmod(pre_commit_hook_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
