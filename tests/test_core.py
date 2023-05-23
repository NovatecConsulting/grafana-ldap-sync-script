from ldap3.core.exceptions import LDAPSocketOpenError

from script import core
from unittest import TestCase
from unittest.mock import patch
from requests.exceptions import ConnectionError


class read_mapping_from_csv(TestCase):
    @patch("script.core.read_csv")
    def test_headers_ignored(self, mock_read_csv):
        mock_read_csv.return_value = [["header1",
                                       "header2",
                                       "header3",
                                       "header4",
                                       "header5",
                                       "header6"]
                                      ]

        mapping = core.read_mapping_from_csv(bind='')

        self.assertTrue("teams" in mapping)
        self.assertTrue("folders" in mapping)
        self.assertFalse(mapping["teams"])
        self.assertFalse(mapping["folders"])

    @patch("script.core.read_csv")
    def test_reads_mapping(self, mock_read_csv):
        mock_read_csv.return_value = [["header1",
                                       "header2",
                                       "header3",
                                       "header4",
                                       "header5",
                                       "header6",
                                       "header7"],
                                      ["test_ldap_group",
                                       "test_grafana_team",
                                       "test_grafana_team-id",
                                       "test_grafana_folder_name",
                                       "test_grafana_folder_uid",
                                       "test_grafana_folder_permission",
                                       "test_grafana_folder_permission_for_viewer"]
                                      ]

        mapping = core.read_mapping_from_csv("")

        self.assertTrue("teams" in mapping)
        self.assertTrue("test_grafana_team" in mapping["teams"])
        self.assertTrue("ldap" in mapping["teams"]["test_grafana_team"])
        self.assertEqual(["test_ldap_group"], mapping["teams"]["test_grafana_team"]["ldap"])
        self.assertTrue("folders" in mapping)
        self.assertTrue("test_grafana_folder_uid" in mapping["folders"])
        self.assertTrue("name" in mapping["folders"]["test_grafana_folder_uid"])
        self.assertTrue("permissions" in mapping["folders"]["test_grafana_folder_uid"])
        self.assertEqual("test_grafana_folder_name", mapping["folders"]["test_grafana_folder_uid"]["name"])
        self.assertEqual([{"teamId": "test_grafana_team", "permission": "test_grafana_folder_permission"},
                        {"role": "Viewer", "permission": "test_grafana_folder_permission_for_viewer"}],
                         mapping["folders"]["test_grafana_folder_uid"]["permissions"])


class add_users(TestCase):
    @patch("script.core.get_members_of_team")
    @patch("script.core.get_users_of_group")
    @patch("script.core.login_taken")
    @patch("script.core.create_user_with_random_pw")
    @patch("script.core.add_user_to_team")
    def test_adding_users(self, mock_add_user_to_team, mock_create_user_with_random_pw, mock_login_taken,
                          mock_get_users_of_group, mock_get_members_of_team):
        ldap_groups = ["group1", "group2"]
        mock_add_user_to_team.return_value = True
        mock_create_user_with_random_pw.return_value = True
        mock_login_taken.return_value = False
        mock_get_users_of_group.return_value = [{"login": "user1"}, {"login": "user2"}]
        mock_get_members_of_team.return_value = [{"login": "user1"}]

        core.add_users("grafana_team", ldap_groups)

        self.assertTrue(mock_create_user_with_random_pw.call_count, 1)
        self.assertTrue(mock_add_user_to_team.call_count, 1)
        mock_create_user_with_random_pw.assert_called_with({"login": "user2"})
        mock_add_user_to_team.assert_called_with("user2", "grafana_team")

    @patch("script.core.get_members_of_team")
    @patch("script.core.get_users_of_group")
    @patch("script.core.login_taken")
    @patch("script.core.create_user_with_random_pw")
    @patch("script.core.add_user_to_team")
    def test_users_already_exist(self, mock_add_user_to_team, mock_create_user_with_random_pw, mock_login_taken,
                                 mock_get_users_of_group, mock_get_members_of_team):
        ldap_groups = ["group1", "group2"]
        mock_add_user_to_team.return_value = True
        mock_create_user_with_random_pw.return_value = True
        mock_login_taken.return_value = False
        mock_get_users_of_group.return_value = [{"login": "user1"}]
        mock_get_members_of_team.return_value = [{"login": "user1"}]

        core.add_users("grafana_team", ldap_groups)

        self.assertFalse(mock_create_user_with_random_pw.called)
        self.assertFalse(mock_add_user_to_team.called)

    @patch("script.core.get_members_of_team")
    @patch("script.core.get_users_of_group")
    @patch("script.core.login_taken")
    @patch("script.core.create_user_with_random_pw")
    @patch("script.core.add_user_to_team")
    def test_no_users(self, mock_add_user_to_team, mock_create_user_with_random_pw, mock_login_taken,
                      mock_get_users_of_group, mock_get_members_of_team):
        ldap_groups = ["group1", "group2"]
        mock_add_user_to_team.return_value = True
        mock_create_user_with_random_pw.return_value = True
        mock_login_taken.return_value = False
        mock_get_users_of_group.return_value = []
        mock_get_members_of_team.return_value = []

        core.add_users("grafana_team", ldap_groups)

        self.assertFalse(mock_create_user_with_random_pw.called)
        self.assertFalse(mock_add_user_to_team.called)


class remove_users(TestCase):
    @patch("script.core.get_members_of_team")
    @patch("script.core.get_users_of_group")
    @patch("script.core.remove_member_from_team")
    def test_removing_users(self, mock_remove_member_from_team, mock_get_users_of_group, mock_get_members_of_team):
        mock_get_members_of_team.return_value = [{"login": "user1"}]
        mock_get_users_of_group.return_value = []
        mock_remove_member_from_team.return_value = True

        core.remove_users("grafana_team", ["group1", "group2"])

        self.assertTrue(mock_remove_member_from_team.call_count, 1)
        mock_remove_member_from_team.assert_called_with("grafana_team", "user1")

    @patch("script.core.get_members_of_team")
    @patch("script.core.get_users_of_group")
    @patch("script.core.remove_member_from_team")
    def test_no_users_to_remove(self, mock_remove_member_from_team, mock_get_users_of_group, mock_get_members_of_team):
        mock_get_members_of_team.return_value = []
        mock_get_users_of_group.return_value = []
        mock_remove_member_from_team.return_value = True

        core.remove_users("grafana_team", ["group1", "group2"])

        self.assertFalse(mock_remove_member_from_team.called)

    @patch("script.core.get_members_of_team")
    @patch("script.core.get_users_of_group")
    @patch("script.core.remove_member_from_team")
    def test_remove_one_keep_one(self, mock_remove_member_from_team, mock_get_users_of_group, mock_get_members_of_team):
        mock_get_members_of_team.return_value = [{"login": "user1"}, {"login": "user2"}]
        mock_get_users_of_group.return_value = [{"login": "user1"}]
        mock_remove_member_from_team.return_value = True

        core.remove_users("grafana_team", ["group1"])

        self.assertTrue(mock_remove_member_from_team.call_count, 1)
        mock_remove_member_from_team.assert_called_with("grafana_team", "user2")

    @patch("script.core.get_members_of_team")
    @patch("script.core.get_users_of_group")
    @patch("script.core.remove_member_from_team")
    def test_remove_one_keep_one(self, mock_remove_member_from_team, mock_get_users_of_group, mock_get_members_of_team):
        mock_get_members_of_team.return_value = [{"login": "user1"}, {"login": "user2"}]
        mock_get_users_of_group.return_value = [{"login": "user1"}]
        mock_remove_member_from_team.return_value = True

        core.remove_users("grafana_team", ["group1"])

        self.assertTrue(mock_remove_member_from_team.call_count, 1)
        mock_remove_member_from_team.assert_called_with("grafana_team", "user2")


class update_teams(TestCase):
    @patch("script.core.create_team")
    @patch("script.core.add_users")
    @patch("script.core.remove_users")
    @patch("script.core.get_id_of_team")
    def test_creates_team(self, mock_get_id_of_team, mock_remove_users, mock_add_users, mock_create_team):
        mock_get_id_of_team.return_value = False
        mock_remove_users.return_value = True
        mock_add_users.return_value = True
        mock_create_team.return_value = True

        core.update_teams({"grafana_team": {"ldap": []}})

        self.assertTrue(mock_create_team.call_count, 1)
        mock_create_team.assert_called_with("grafana_team", "")

    @patch("script.core.create_team")
    @patch("script.core.add_users")
    @patch("script.core.remove_users")
    @patch("script.core.get_id_of_team")
    def test_does_not_create_team(self, mock_get_id_of_team, mock_remove_users, mock_add_users, mock_create_team):
        mock_get_id_of_team.return_value = True
        mock_remove_users.return_value = True
        mock_add_users.return_value = True
        mock_create_team.return_value = True

        core.update_teams({"grafana_team": {"ldap": []}})

        self.assertFalse(mock_create_team.called)

    @patch("script.core.create_team")
    @patch("script.core.add_users")
    @patch("script.core.remove_users")
    @patch("script.core.get_id_of_team")
    def test_add_and_remove_called(self, mock_get_id_of_team, mock_remove_users, mock_add_users, mock_create_team):
        mock_get_id_of_team.return_value = True
        mock_remove_users.return_value = True
        mock_add_users.return_value = True
        mock_create_team.return_value = True

        core.update_teams({"grafana_team": {"ldap": ["ldap1", "ldap2"]}})

        self.assertTrue(mock_add_users.call_count, 1)
        self.assertTrue(mock_remove_users.call_count, 1)
        mock_add_users.assert_called_with("grafana_team", ["ldap1", "ldap2"])
        mock_remove_users.assert_called_with("grafana_team", ["ldap1", "ldap2"])


class update_folders(TestCase):
    @patch("script.core.exists_folder")
    @patch("script.core.create_folder")
    @patch("script.core.get_id_of_team")
    @patch("script.core.update_folder_permissions")
    def test_folder_created(self, mock_update_folder_permissions, mock_get_id_of_team, mock_create_folder,
                            mock_exists_folder):
        mock_exists_folder.return_value = False
        mock_create_folder.return_value = True
        mock_get_id_of_team.return_value = "1"
        mock_update_folder_permissions.return_value = True
        test_folders = {"folder_1":
            {
                "name": "folder1",
                "permissions": [{"teamId": "grafana_team", "permission": "View"}]
            }
        }

        core.update_folders(test_folders)

        self.assertTrue(mock_create_folder.call_count, 1)
        mock_create_folder.assert_called_with("folder1", "folder_1")
        self.assertTrue(mock_create_folder.call_count, 1)
        mock_update_folder_permissions.assert_called_with("folder_1", [{"teamId": "1", "permission": 1}])

    @patch("script.core.exists_folder")
    @patch("script.core.create_folder")
    @patch("script.core.get_id_of_team")
    @patch("script.core.update_folder_permissions")
    def test_edit_permission_resolved(self, mock_update_folder_permissions, mock_get_id_of_team, mock_create_folder,
                                      mock_exists_folder):
        mock_exists_folder.return_value = False
        mock_create_folder.return_value = True
        mock_get_id_of_team.return_value = "1"
        mock_update_folder_permissions.return_value = True
        test_folders = {"folder_1":
            {
                "name": "folder1",
                "permissions": [{"teamId": "grafana_team", "permission": "Edit"}]
            }
        }

        core.update_folders(test_folders)

        self.assertTrue(mock_create_folder.call_count, 1)
        mock_create_folder.assert_called_with("folder1", "folder_1")
        self.assertTrue(mock_create_folder.call_count, 1)
        mock_update_folder_permissions.assert_called_with("folder_1", [{"teamId": "1", "permission": 2}])

    @patch("script.core.exists_folder")
    @patch("script.core.create_folder")
    @patch("script.core.get_id_of_team")
    @patch("script.core.update_folder_permissions")
    def test_admin_permission_resolved(self, mock_update_folder_permissions, mock_get_id_of_team, mock_create_folder,
                                       mock_exists_folder):
        mock_exists_folder.return_value = False
        mock_create_folder.return_value = True
        mock_get_id_of_team.return_value = "1"
        mock_update_folder_permissions.return_value = True
        test_folders = {"folder_1":
            {
                "name": "folder1",
                "permissions": [{"teamId": "grafana_team", "permission": "Admin"}]
            }
        }

        core.update_folders(test_folders)

        self.assertTrue(mock_create_folder.call_count, 1)
        self.assertTrue(mock_create_folder.call_count, 1)
        mock_create_folder.assert_called_with("folder1", "folder_1")
        mock_update_folder_permissions.assert_called_with("folder_1", [{"teamId": "1", "permission": 4}])


class delete_unmapped_teams(TestCase):
    @patch("script.core.get_all_teams")
    @patch("script.core.delete_team_by_name")
    def test_removes_team(self, mock_delete_team_by_name, mock_get_all_teams):
        mock_delete_team_by_name.return_value = True
        mock_get_all_teams.return_value = [{"name": "delete_me"}]
        test_mapping = {"keep_me": []}

        core.delete_unmapped_teams(test_mapping)

        self.assertTrue(mock_delete_team_by_name.call_count, 1)
        mock_delete_team_by_name.assert_called_with("delete_me")

    @patch("script.core.get_all_teams")
    @patch("script.core.delete_team_by_name")
    def test_nothing_to_remove(self, mock_delete_team_by_name, mock_get_all_teams):
        mock_delete_team_by_name.return_value = True
        mock_get_all_teams.return_value = [{"name": "keep_me"}]
        test_mapping = {"keep_me": []}

        core.delete_unmapped_teams(test_mapping)

        self.assertFalse(mock_delete_team_by_name.called)


class get_users_of_used_ldap_groups(TestCase):
    @patch("script.core.get_users_of_group")
    def test_returns_users_as_expected(self, mock_get_users_of_group):
        mapping = {"team": {"ldap": ["group1", "group2"]}}
        mock_get_users_of_group.return_value = ["user1", "user2"]

        output = core.get_users_of_used_ldap_groups(mapping)

        self.assertEqual(output, ["user1", "user2"])
        self.assertEqual(mock_get_users_of_group.call_count, 2)
        mock_get_users_of_group.asser_called_with("group1")
        mock_get_users_of_group.asser_called_with("group2")


class delete_unmapped_users(TestCase):
    @patch("script.core.get_all_users")
    @patch("script.core.get_users_of_used_ldap_groups")
    @patch("script.core.delete_user_by_login")
    def test_deletes_users(self, mock_delete_user_by_login, mock_get_users_of_used_ldap_groups, mock_get_all_users):
        mock_get_all_users.return_value = [{"login": "user1"}, {"login": "user2"}]
        mock_get_users_of_used_ldap_groups.return_value = [{"login": "user1"}]
        mock_delete_user_by_login.return_value = True

        core.delete_unmapped_users({})

        self.assertEqual(mock_delete_user_by_login.call_count, 1)
        mock_delete_user_by_login.asser_called_with("user2")

    @patch("script.core.get_all_users")
    @patch("script.core.get_users_of_used_ldap_groups")
    @patch("script.core.delete_user_by_login")
    def test_nothing_to_delete(self, mock_delete_user_by_login, mock_get_users_of_used_ldap_groups, mock_get_all_users):
        mock_get_all_users.return_value = [{"login": "user1"}]
        mock_get_users_of_used_ldap_groups.return_value = [{"login": "user1"}]
        mock_delete_user_by_login.return_value = True

        core.delete_unmapped_users({})

        self.assertFalse(mock_delete_user_by_login.called)


class export(TestCase):
    @patch("script.core.lock")
    @patch("script.core.config")
    @patch("script.core.setup_grafana")
    @patch("script.core.read_mapping_from_csv")
    @patch("script.core.update_teams")
    @patch("script.core.update_folders")
    @patch("script.core.remove_unused_items")
    @patch("script.core.unlock")
    @patch("script.core.setup_ldap")
    def test_locks_and_unlocks(self, mock_setup_ldap, mock_unlock, mock_remove_unused_items, mock_update_folders, mock_update_teams,
                               mock_read_mapping_from_csv, mock_setup_grafana, mock_config, mock_lock):
        mock_setup_ldap.return_value = True
        mock_unlock.return_value = True
        mock_remove_unused_items.return_value = True
        mock_update_folders.return_value = True
        mock_update_teams.return_value = True
        mock_read_mapping_from_csv.return_value = {"teams": {}, "folders": {}}
        mock_setup_grafana.return_value = True
        mock_config.return_value = True
        mock_lock.return_value = True

        core.startUserSync("", "", "")

        self.assertEqual(mock_lock.call_count, 1)
        self.assertEqual(mock_unlock.call_count, 1)

    @patch("script.core.lock")
    @patch("script.core.config")
    @patch("script.core.setup_grafana")
    @patch("script.core.read_mapping_from_csv", side_effect=ConnectionError('whoops'))
    @patch("script.core.update_teams")
    @patch("script.core.update_folders")
    @patch("script.core.remove_unused_items")
    @patch("script.core.unlock")
    @patch("script.core.setup_ldap")
    def test_locks_and_unlocks_on_connection_error(self, mock_setup_ldap, mock_unlock, mock_remove_unused_items, mock_update_folders,
                                                   mock_update_teams, mock_read_mapping_from_csv, mock_setup_grafana,
                                                   mock_config, mock_lock):
        mock_setup_ldap.return_value = True
        mock_unlock.return_value = True
        mock_remove_unused_items.return_value = True
        mock_update_folders.return_value = True
        mock_read_mapping_from_csv.return_value = {"teams": {}, "folders": {}}
        mock_setup_grafana.return_value = True
        mock_config.return_value = True
        mock_lock.return_value = True

        core.startUserSync("", "", "")

        self.assertEqual(mock_lock.call_count, 1)
        self.assertEqual(mock_unlock.call_count, 1)

    @patch("script.core.lock")
    @patch("script.core.config")
    @patch("script.core.setup_grafana")
    @patch("script.core.read_mapping_from_csv")
    @patch("script.core.update_teams", side_effect=LDAPSocketOpenError('whoops'))
    @patch("script.core.update_folders")
    @patch("script.core.remove_unused_items")
    @patch("script.core.unlock")
    @patch("script.core.setup_ldap")
    def test_locks_and_unlocks_on_LDAPSocketOpenError(self, mock_setup_ldap, mock_unlock, mock_remove_unused_items, mock_update_folders,
                                                      mock_update_teams, mock_read_mapping_from_csv,
                                                      mock_setup_grafana,
                                                      mock_config, mock_lock):
        mock_setup_ldap.return_value = True
        mock_unlock.return_value = True
        mock_remove_unused_items.return_value = True
        mock_update_folders.return_value = True
        mock_read_mapping_from_csv.return_value = {"teams": {}, "folders": {}}
        mock_setup_grafana.return_value = True
        mock_config.return_value = True
        mock_lock.return_value = True

        core.startUserSync("", "", "")

        self.assertEqual(mock_lock.call_count, 1)
        self.assertEqual(mock_unlock.call_count, 1)

    @patch("script.core.lock")
    @patch("script.core.config")
    @patch("script.core.setup_grafana")
    @patch("script.core.read_mapping_from_csv")
    @patch("script.core.update_teams")
    @patch("script.core.update_folders")
    @patch("script.core.remove_unused_items")
    @patch("script.core.unlock")
    def test_nothing_called_when_locked(self, mock_unlock, mock_remove_unused_items, mock_update_folders,
                                        mock_update_teams, mock_read_mapping_from_csv,
                                        mock_setup_grafana,
                                        mock_config, mock_lock):
        mock_unlock.return_value = True
        mock_remove_unused_items.return_value = True
        mock_update_folders.return_value = True
        mock_read_mapping_from_csv.return_value = {"teams": {}, "folders": {}}
        mock_setup_grafana.return_value = True
        mock_config.return_value = True
        mock_lock.return_value = False

        core.startUserSync("", "", "")

        self.assertEqual(mock_lock.call_count, 1)
        self.assertFalse(mock_remove_unused_items.called)
        self.assertFalse(mock_update_folders.called)
        self.assertFalse(mock_update_teams.called)
        self.assertFalse(mock_read_mapping_from_csv.called)
        self.assertFalse(mock_setup_grafana.called)
        self.assertFalse(mock_config.called)
        self.assertFalse(mock_unlock.called)
