from unittest import TestCase
from unittest.mock import patch, Mock

from grafana_api.grafana_api import GrafanaClientError

from script import grafana


class delete_team_by_name(TestCase):
    @patch("script.grafana.grafana_api")
    def test_deletes_team(self, mock_grafana_api):
        mock_grafana_api.teams = Mock()
        mock_grafana_api.teams.get_team_by_name.return_value = [{"id": "my_team_id"}]

        output = grafana.delete_team_by_name("my_team")

        self.assertEqual(output, True)
        self.assertEqual(mock_grafana_api.teams.delete_team.call_count, 1)
        mock_grafana_api.teams.delete_team.assert_called_with("my_team_id")

    @patch("script.grafana.grafana_api")
    def test_no_team_to_delete(self, mock_grafana_api):
        mock_grafana_api.teams = Mock()
        mock_grafana_api.teams.get_team_by_name.return_value = []

        output = grafana.delete_team_by_name("my_team")

        self.assertEqual(output, False)
        self.assertFalse(mock_grafana_api.teams.delete_team.called)


class delete_user_by_login(TestCase):
    @patch("script.grafana.grafana_api")
    def test_does_not_delete_admin(self, mock_grafana_api):
        mock_grafana_api.admin = Mock()
        mock_grafana_api.admin.delete_user.return_value = True

        output = grafana.delete_user_by_login("admin")

        self.assertFalse(output)

    @patch("script.grafana.grafana_api")
    def test_deletes_user(self, mock_grafana_api):
        mock_grafana_api.admin = Mock()
        mock_grafana_api.admin.delete_user.return_value = True
        mock_grafana_api.users.find_user = Mock()
        mock_grafana_api.users.find_user.return_value = {"id": "id_delete_me"}

        output = grafana.delete_user_by_login("delete_me")

        self.assertTrue(output)
        self.assertEqual(mock_grafana_api.admin.delete_user.call_count, 1)
        mock_grafana_api.admin.delete_user.called_with("id_delete_me")
        self.assertEquals(mock_grafana_api.users.find_user.call_count, 1)
        mock_grafana_api.users.find_user.called_with("delete_me")


class create_folder(TestCase):
    @patch("script.grafana.grafana_api")
    def test_creates_folder(self, mock_grafana_api):
        mock_grafana_api.folder.create_folder = Mock()
        mock_grafana_api.folder.create_folder.return_value = True

        output = grafana.create_folder("foo", "bar")

        self.assertTrue(output)
        self.assertEqual(mock_grafana_api.folder.create_folder.call_count, 1)
        mock_grafana_api.folder.create_folder.assert_called_with("foo", "bar")

    @patch("script.grafana.grafana_api")
    def test_catches_exception(self, mock_grafana_api):
        mock_grafana_api.folder.create_folder = Mock()
        mock_grafana_api.folder.create_folder.side_effect = GrafanaClientError("something", "went", "wrong")

        output = grafana.create_folder("foo", "bar")

        self.assertFalse(output)
        self.assertEqual(mock_grafana_api.folder.create_folder.call_count, 1)
        mock_grafana_api.folder.create_folder.assert_called_with("foo", "bar")


class get_members_of_team(TestCase):
    @patch("script.grafana.grafana_api")
    def test_returns_members_correctly(self, mock_grafana_api):
        mock_grafana_api.teams.get_team_members = Mock()
        mock_grafana_api.teams.get_team_members.return_value = [{"login": "user_login",
                                                                 }
                                                                ]

        output = grafana.get_members_of_team("my_team")

        self.assertEqual(output, [{"login": "user_login"}])


class login_taken(TestCase):
    @patch("script.grafana.grafana_api")
    def test_login_is_taken(self, mock_grafana_api):
        mock_grafana_api.users.find_user = Mock()
        mock_grafana_api.users.find_user.return_value = ""

        output = grafana.login_taken("foo")

        self.assertTrue(output)

    @patch("script.grafana.grafana_api")
    def test_login_is_not_taken(self, mock_grafana_api):
        mock_grafana_api.users.find_user = Mock()
        mock_grafana_api.users.find_user.side_effect = GrafanaClientError("user", "not", "found")

        output = grafana.login_taken("foo")

        self.assertFalse(output)


class exists_folder(TestCase):
    @patch("script.grafana.grafana_api")
    def test_login_is_taken(self, mock_grafana_api):
        mock_grafana_api.folder.get_folder = Mock()
        mock_grafana_api.folder.get_folder.return_value = ""

        output = grafana.exists_folder("foo")

        self.assertTrue(output)

    @patch("script.grafana.grafana_api")
    def test_login_is_not_taken(self, mock_grafana_api):
        mock_grafana_api.folder.get_folder = Mock()
        mock_grafana_api.folder.get_folder.side_effect = GrafanaClientError("user", "not", "found")

        output = grafana.exists_folder("foo")

        self.assertFalse(output)


class get_id_of_team(TestCase):
    @patch("script.grafana.grafana_api")
    def test_team_exists(self, mock_grafana_api):
        mock_grafana_api.teams.get_team_by_name = Mock()
        mock_grafana_api.teams.get_team_by_name.return_value = [{"id": "my_team"}]

        output = grafana.get_id_of_team("my_team")

        self.assertEqual(output, "my_team")

    @patch("script.grafana.grafana_api")
    def test_team_not_existing(self, mock_grafana_api):
        mock_grafana_api.teams.get_team_by_name = Mock()
        mock_grafana_api.teams.get_team_by_name.return_value = []

        output = grafana.get_id_of_team("my_team")

        self.assertFalse(output)


class update_folder_permissions(TestCase):
    @patch("script.grafana.grafana_api")
    def test_update_input(self, mock_grafana_api):
        mock_grafana_api.folder.update_folder_permissions = Mock()
        mock_grafana_api.folder.update_folder_permissions.return_value = []

        grafana.update_folder_permissions("my_folder", [
            {
                "id": "my_id",
                "permission": 1
            }
        ])

        self.assertEqual(mock_grafana_api.folder.update_folder_permissions.call_count, 1)
        mock_grafana_api.folder.update_folder_permissions.assert_called_with("my_folder",
                                                                             {"items": [
                                                                                 {"id": "my_id",
                                                                                  "permission": 1
                                                                                  }
                                                                             ]
                                                                             })
