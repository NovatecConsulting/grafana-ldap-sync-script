from unittest import TestCase
from unittest.mock import patch, Mock

from ldap3 import ALL

from script import ldap


class get_ldap_connection(TestCase):
    @patch("script.ldap.Connection", autospec=True)
    @patch("script.ldap.Server", autospec=True)
    @patch("script.ldap.config", autospec=True)
    def test_creates_connection(self, mock_config, mock_server, mock_connection):
        mock_config_object = Mock()
        mock_config_object.LDAP_SERVER_URL = "my_url"
        mock_config_object.LDAP_USER = "my_user"
        mock_config_object.LDAP_PASSWORD = "my_password"
        mock_config.return_value = mock_config_object
        mock_server_object = Mock()
        mock_server.return_value = mock_server_object
        mock_connection.return_value = True

        output = ldap.get_ldap_connection()

        self.assertEqual(output, True)
        self.assertEqual(mock_config.call_count, 1)
        self.assertEqual(mock_server.call_count, 1)
        self.assertEqual(mock_connection.call_count, 1)
        mock_server.assert_called_with("my_url", get_info=ALL)
        mock_connection.assert_called_with(mock_server_object, "my_user", "my_password", auto_bind=True)


class get_users_of_group(TestCase):
    @patch("script.ldap.get_ldap_connection")
    @patch("script.ldap.configuration")
    def test_retrieves_users(self, mock_config, mock_get_ldap_connection):
        mock_config_object = Mock()
        mock_config_object.LDAP_USER_SEARCH_BASE.value = "my_search_base"
        mock_config_object.LDAP_GROUP_DESCRIPTOR = "my_group"
        mock_config.return_value = mock_config_object
        mock_connection = Mock()
        mock_connection.extend.standard.paged_search.return_value = [
            {"attributes": {"cn": ["my_cn"], "mail": ["my_mail"], "uid": ["my_uid"],
                            "another_attribute": ["i_am_not_retrieved"]}}]
        mock_get_ldap_connection.return_value = mock_connection

        output = ldap.get_users_of_group("test_group")

        self.assertEqual([{"name": "my_cn", "mail": "my_mail", "login": "my_uid"}], output)
