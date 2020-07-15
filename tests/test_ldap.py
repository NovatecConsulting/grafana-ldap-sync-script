from unittest import TestCase
from unittest.mock import patch, Mock

from ldap3 import ALL, NTLM

from script import ldap


class get_ldap_connection(TestCase):
    @patch("script.ldap.Connection", autospec=True)
    @patch("script.ldap.Server", autospec=True)
    @patch("script.ldap.configuration")
    def test_creates_connection(self, mock_configuration, mock_server, mock_connection):
        mock_configuration.LDAP_SERVER_URL = "my_url"
        mock_configuration.LDAP_USER = "my_user"
        mock_configuration.LDAP_PASSWORD = "my_password"
        mock_server_object = Mock()
        mock_server.return_value = mock_server_object
        mock_connection.return_value = True

        output = ldap.get_ldap_connection()

        self.assertEqual(output, True)
        self.assertEqual(mock_server.call_count, 1)
        self.assertEqual(mock_connection.call_count, 1)
        mock_server.assert_called_with("my_url", get_info=ALL)
        mock_connection.assert_called_with(mock_server_object, "my_user", "my_password", auto_bind=True, read_only=True)


class get_ntml_connection(TestCase):
    @patch("script.ldap.Connection", autospec=True)
    @patch("script.ldap.Server", autospec=True)
    @patch("script.ldap.configuration")
    def test_creates_connection(self, mock_configuration, mock_server, mock_connection):
        mock_configuration.LDAP_SERVER_URL = "my_url"
        mock_configuration.LDAP_USER = "my_user"
        mock_configuration.LDAP_PASSWORD = "my_password"
        mock_server_object = Mock()
        mock_server.return_value = mock_server_object
        mock_connection.return_value = True

        output = ldap.get_ntlm_connection()

        self.assertEqual(output, True)
        self.assertEqual(mock_server.call_count, 1)
        self.assertEqual(mock_connection.call_count, 1)
        mock_server.assert_called_with("my_url", get_info=ALL)
        mock_connection.assert_called_with(mock_server_object, user="my_url\\my_user", password="my_password",
                                           authentication=NTLM, read_only=True)


class fetch_users_of_group(TestCase):
    @patch("script.ldap.get_ntlm_connection")
    @patch("script.ldap.configuration")
    def test_retrieves_users_NTML(self, mock_configuration, mock_get_ntlm_connection):
        mock_configuration.LDAP_USER_SEARCH_BASE.value = "my_search_base"
        mock_configuration.LDAP_GROUP_DESCRIPTOR = "my_group"
        mock_configuration.LDAP_IS_NTLM = True
        mock_configuration.LDAP_MEMBER_ATTRIBUTE = "member"
        mock_configuration.LDAP_USER_LOGIN_ATTRIBUTE = "uid"
        mock_connection = Mock()
        mock_connection.extend.standard.paged_search.return_value = [
            {"attributes": {"member": ["uid=my_login, foo=bar"],
                            "another_attribute": ["i_am_not_retrieved"]}}]
        mock_get_ntlm_connection.return_value = mock_connection

        output = ldap.fetch_users_of_group("test_group")

        self.assertEqual([{"login": "my_login"}], output)
        self.assertEqual(mock_get_ntlm_connection.call_count, 1)

    @patch("script.ldap.get_ldap_connection")
    @patch("script.ldap.configuration")
    def test_retrieves_users(self, mock_configuration, mock_get_ldap_connection):
        mock_configuration.LDAP_USER_SEARCH_BASE.value = "my_search_base"
        mock_configuration.LDAP_GROUP_DESCRIPTOR = "my_group"
        mock_configuration.LDAP_IS_NTLM = False
        mock_configuration.LDAP_MEMBER_ATTRIBUTE = "member"
        mock_configuration.LDAP_USER_LOGIN_ATTRIBUTE = "uid"
        mock_connection = Mock()
        mock_connection.extend.standard.paged_search.return_value = [
            {"attributes": {"member": ["uid=my_login, foo=bar"],
                            "another_attribute": ["i_am_not_retrieved"]}}]
        mock_get_ldap_connection.return_value = mock_connection

        output = ldap.fetch_users_of_group("test_group")

        self.assertEqual([{"login": "my_login"}], output)
        self.assertEqual(mock_get_ldap_connection.call_count, 1)


class get_users_of_group(TestCase):
    @patch("script.ldap.fetch_users_of_group")
    def test_group_not_cached(self, mock_fetch_users_of_group):
        mock_fetch_users_of_group.return_value = "cache me if you can!"

        output = ldap.get_users_of_group("my_group")

        self.assertEqual(output, "cache me if you can!")
        self.assertEqual(mock_fetch_users_of_group.call_count, 1)
        mock_fetch_users_of_group.asset_called_with("my_group")

    @patch("script.ldap.fetch_users_of_group")
    @patch("script.ldap.user_cache")
    def test_group_cached(self, mock_user_cache, mock_fetch_users_of_group):
        mock_fetch_users_of_group.return_value = "cache me if you can!"
        cache = {"my_group": "i am already cached!"}
        mock_user_cache.__getitem__.side_effect = cache.__getitem__
        mock_user_cache.__iter__.side_effect = cache.__iter__
        mock_user_cache.__contains__.side_effect = cache.__contains__

        output = ldap.get_users_of_group("my_group")

        self.assertEqual(output, "i am already cached!")
        self.assertFalse(mock_fetch_users_of_group.called)
