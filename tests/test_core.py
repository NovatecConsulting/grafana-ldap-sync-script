import os

from mockito import ANY

import script
from script import core, ldap, grafana, config
from unittest import TestCase, mock
from mockito import *
from unittest.mock import patch, Mock
from unittest.mock import create_autospec


class read_mapping_from_csv(TestCase):
    def test_headers_ignored(self):
        when2(core.read_csv).thenReturn([["header1",
                                          "header2",
                                          "header3",
                                          "header4",
                                          "header5",
                                          "header6"]
                                         ])

        mapping = core.read_mapping_from_csv()

        self.assertTrue("teams" in mapping)
        self.assertTrue("folders" in mapping)
        self.assertFalse(mapping["teams"])
        self.assertFalse(mapping["folders"])
        unstub()

    def test_reads_mapping(self):
        when2(core.read_csv).thenReturn([["header1",
                                          "header2",
                                          "header3",
                                          "header4",
                                          "header5",
                                          "header6"],
                                         ["test_ldap_group",
                                          "test_grafana_team",
                                          "test_grafana_team-id",
                                          "test_grafana_folder_name",
                                          "test_grafana_folder_uid",
                                          "test_grafana_folder_permission"]
                                         ])

        mapping = core.read_mapping_from_csv()

        self.assertTrue("teams" in mapping)
        self.assertTrue("test_grafana_team" in mapping["teams"])
        self.assertTrue("ldap" in mapping["teams"]["test_grafana_team"])
        self.assertEqual(["test_ldap_group"], mapping["teams"]["test_grafana_team"]["ldap"])
        self.assertTrue("folders" in mapping)
        self.assertTrue("test_grafana_folder_uid" in mapping["folders"])
        self.assertTrue("name" in mapping["folders"]["test_grafana_folder_uid"])
        self.assertTrue("permissions" in mapping["folders"]["test_grafana_folder_uid"])
        self.assertEqual("test_grafana_folder_name", mapping["folders"]["test_grafana_folder_uid"]["name"])
        self.assertEqual([{"teamId": "test_grafana_team", "permission": "test_grafana_folder_permission"}],
                         mapping["folders"]["test_grafana_folder_uid"]["permissions"])
        unstub()


class t_add_users(TestCase):
    @patch("script.grafana")
    def test_users(self, MockGrafana):
        ldap_groups = ["group1", "group2"]
        group1 = ["user1", "user2"]
        group2 = ["user3"]
        #grafana.get_members_of_team("grafana_team")
        MockGrafana.get_members_of_team.return_value = ["user1"]
        print(MockGrafana.get_members_of_team(""))

        #core.add_users("grafana_team", ldap_groups)

        # verify(grafana.create_user_with_random_pw, 2)
        # unstub()
