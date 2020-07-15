from unittest import TestCase
from unittest.mock import patch, Mock

from script import helpers


class lock(TestCase):
    @patch("script.helpers.os.path.exists")
    @patch("script.helpers.open")
    def test_is_locked(self, mock_open, mock_exists):
        mock_exists.return_value = True

        output = helpers.lock()

        self.assertEqual(output, False)

    @patch("script.helpers.os.path.exists")
    @patch("script.helpers.open")
    def test_locks(self, mock_open, mock_exists):
        mock_exists.return_value = False
        mock_file = Mock()
        mock_file.close().return_value = True
        mock_open.return_value = mock_file

        output = helpers.lock()

        self.assertEqual(output, True)


class unlock(TestCase):
    @patch("script.helpers.os.remove")
    def test_removes_lock(self, mock_remove):
        mock_remove.return_value = True

        helpers.unlock()

        self.assertTrue(mock_remove.called)

