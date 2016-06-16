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

from unittest import TestCase

import mock

from precog import isort_git_hook, stash_unstaged


class TestStashUntaged(TestCase):

    @mock.patch('precog.subprocess.check_call')
    def test_not_is_needed(self, m_check_call):
        """If we pass is_needed=False, then the context manager should do
        nothing, and should be marked as a success.

        """

        with stash_unstaged(is_needed=False):
            # Should not have invoked any subprocess calls when
            # entering.
            m_check_call.assert_not_called()

        # Should still have made none by the end.
        m_check_call.assert_not_called()

    @mock.patch('precog._datetime_token', mock.Mock(return_value='2016-01-01 12:34:56.789012'))
    @mock.patch('precog.get_lines')
    @mock.patch('precog.subprocess.call', return_value=0)
    @mock.patch('precog.subprocess.check_call')
    def test_stash_and_pop(self, m_check_call, m_call, m_get_lines):
        stash_save_message = 'Isort save - 2016-01-01 12:34:56.789012'

        m_get_lines.return_value = [
            'stash@{0}: On thisbranch: ' + stash_save_message,
            'stash@{1}: On mybranch: my stash',
            'stash@{2}: On mybranch2: my stash2',
        ]

        with stash_unstaged(is_needed=True) as ctx:
            # On entering, should have made a call to `git stash` to
            # save the current unstaged changes with the message.
            m_check_call.assert_called_with(['git', 'stash', 'save', '-k', stash_save_message])

        m_call.assert_called_with(['git', 'stash', 'pop', 'stash@{0}'])
        assert ctx.success

    @mock.patch('precog._datetime_token', mock.Mock(return_value='2016-01-01 12:34:56.789012'))
    @mock.patch('precog.get_lines')
    @mock.patch('precog.subprocess.call', return_value=1)  # error when popping stash
    @mock.patch('precog.subprocess.check_call')
    def test_stash_and_pop_with_error(self, m_check_call, m_call, m_get_lines):
        stash_save_message = 'Isort save - 2016-01-01 12:34:56.789012'

        m_get_lines.return_value = [
            'stash@{0}: On thisbranch: ' + stash_save_message,
            'stash@{1}: On mybranch: my stash',
            'stash@{2}: On mybranch2: my stash2',
        ]

        with stash_unstaged(is_needed=True) as ctx:
            # On entering, should have made a call to `git stash` to
            # save the current unstaged changes with the message.
            m_check_call.assert_called_with(['git', 'stash', 'save', '-k', stash_save_message])

        m_call.assert_called_with(['git', 'stash', 'pop', 'stash@{0}'])
        assert not ctx.success


class TestIsortGitHook(TestCase):

    @mock.patch('precog.stash_unstaged')
    @mock.patch('precog.get_output', return_value=b'content')
    @mock.patch('precog.SortImports', return_value=mock.Mock(incorrectly_sorted=False))
    @mock.patch('precog.get_lines')
    def test_not_strict_not_force_with_no_errors(self, m_get_lines, m_sortimports, m_get_output, m_stash_unstaged):
        m_get_lines.return_value = [
            'file1.py',
            'file2.py',
        ]
        m_stash_unstaged.__enter__.return_value = mock.Mock(success=True)

        errors = isort_git_hook(strict=False, force=False)

        assert m_get_lines.called

        m_get_output.assert_has_calls([
            mock.call('git show :file1.py'),
            mock.call('git show :file2.py'),
        ])

        m_sortimports.assert_has_calls([
            mock.call(
                file_path='file1.py',
                file_contents=u'content',
                check=True),
            mock.call(
                file_path='file2.py',
                file_contents=u'content',
                check=True),
        ])

        assert m_stash_unstaged.called_with(is_needed=False)

        assert errors == 0

    @mock.patch('precog.stash_unstaged')
    @mock.patch('precog.get_output', return_value=b'content')
    @mock.patch('precog.SortImports', return_value=mock.Mock(incorrectly_sorted=True))  # Errors
    @mock.patch('precog.get_lines')
    def test_not_strict_not_force_with_errors(self, m_get_lines, m_sortimports, m_get_output, m_stash_unstaged):
        m_get_lines.return_value = [
            'file1.py',
            'file2.py',
        ]
        m_stash_unstaged.__enter__.return_value = mock.Mock(success=True)

        errors = isort_git_hook(strict=False, force=False)

        assert m_get_lines.called

        m_get_output.assert_has_calls([
            mock.call('git show :file1.py'),
            mock.call('git show :file2.py'),
        ])

        m_sortimports.assert_has_calls([
            mock.call(
                file_path='file1.py',
                file_contents=u'content',
                check=True),
            mock.call(
                file_path='file2.py',
                file_contents=u'content',
                check=True),
        ])

        assert m_stash_unstaged.called_with(is_needed=False)

        # But strict is false, so should still return 0
        assert errors == 0

    @mock.patch('precog.stash_unstaged')
    @mock.patch('precog.get_output', return_value=b'content')
    @mock.patch('precog.SortImports', return_value=mock.Mock(incorrectly_sorted=True))  # Errors
    @mock.patch('precog.get_lines')
    def test_strict_not_force_with_errors(self, m_get_lines, m_sortimports, m_get_output, m_stash_unstaged):
        m_get_lines.return_value = [
            'file1.py',
            'file2.py',
        ]
        m_stash_unstaged.__enter__.return_value = mock.Mock(success=True)

        # Strict is enabled, so should return the errors
        errors = isort_git_hook(strict=True, force=False)

        assert m_get_lines.called

        m_get_output.assert_has_calls([
            mock.call('git show :file1.py'),
            mock.call('git show :file2.py'),
        ])

        m_sortimports.assert_has_calls([
            mock.call(
                file_path='file1.py',
                file_contents=u'content',
                check=True),
            mock.call(
                file_path='file2.py',
                file_contents=u'content',
                check=True),
        ])

        assert m_stash_unstaged.called_with(is_needed=False)

        # But strict is false, so should still return 0
        assert errors == 2

    @mock.patch('precog.subprocess.check_call')
    @mock.patch('precog.stash_unstaged')
    @mock.patch('precog.SortImports', return_value=mock.Mock(incorrectly_sorted=False))
    @mock.patch('precog.get_lines')
    def test_strict_and_force_with_no_errors(self, m_get_lines, m_sortimports, m_stash_unstaged, m_check_call):
        m_get_lines.return_value = [
            'file1.py',
            'file2.py',
        ]
        m_stash_unstaged.__enter__.return_value = mock.Mock(success=True)

        # Strict is enabled, so should return the errors
        errors = isort_git_hook(strict=True, force=True)

        assert m_get_lines.called

        m_sortimports.assert_has_calls([
            # Should get called twice, once when sorting inside the
            # context manager, then again outside after the stash is
            # popped.
            mock.call('file1.py'),
            mock.call('file2.py'),
            mock.call('file1.py'),
            mock.call('file2.py'),
        ])

        m_check_call.assert_has_calls([
            mock.call(['git', 'add', 'file1.py']),
            mock.call(['git', 'add', 'file2.py']),
        ])

        assert m_stash_unstaged.called_with(is_needed=True)

        assert errors == 0

    @mock.patch('precog.subprocess.check_call')
    @mock.patch('precog.stash_unstaged')
    @mock.patch('precog.SortImports', return_value=mock.Mock(incorrectly_sorted=False))
    @mock.patch('precog.get_lines')
    def test_strict_and_force_with_stash_pop_error(self, m_get_lines, m_sortimports, m_stash_unstaged, m_check_call):
        m_get_lines.return_value = [
            'file1.py',
            'file2.py',
        ]
        # Make the stash report as being unable to pop cleanly.
        m_stash_unstaged.__enter__.return_value = mock.Mock(success=False)

        # Strict is enabled, so should return the errors
        errors = isort_git_hook(strict=True, force=True)

        assert m_get_lines.called

        m_sortimports.assert_has_calls([
            # Should only be called once - inside the context
            # manager. Should not apply these again outside after the
            # stash-pop as it did not apply cleanly. We do not want to
            # run isort on a file with conflicts.
            mock.call('file1.py'),
            mock.call('file2.py'),
        ])

        m_check_call.assert_has_calls([
            mock.call(['git', 'add', 'file1.py']),
            mock.call(['git', 'add', 'file2.py']),
        ])

        assert m_stash_unstaged.called_with(is_needed=True)

        assert errors == 0
