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
import precog

defaults = dict()

if __name__ == '__main__':
    precog.hook(**defaults)
'''


def install_git_hook():
    pre_commit_hook_path = hooks.find_vcs()
    if os.path.exists(pre_commit_hook_path):
        sys.exit('Error: hook already exists ({})'.format(pre_commit_hook_path))
    with open(pre_commit_hook_path, 'w') as fd:
        fd.write(git_hook_file)
    os.chmod(pre_commit_hook_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
