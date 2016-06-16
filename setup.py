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

from setuptools import find_packages, setup


setup(
    name='precog',
    version='0.0.1',
    author='Isotoma Limited',
    author_email='support@isotoma.com',
    description='Git-hooks for flake8, isort and eslint',
    url='https://github.com/isotoma/precog',
    packages=find_packages(),
    test_suite='tests',
    install_requires=[
        # These can probably be relaxed.
        'isort>=4.2.2',
        'flake8>=2.4.1',
    ],
    tests_require=['mock'],
    license="Apache Software License",
    entry_points='''
    [console_scripts]
    precog = precog.install:install_git_hook
    '''
)
