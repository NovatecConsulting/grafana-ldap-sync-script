from ldap3 import Server, Connection, ALL, SUBTREE, NTLM
import logging

from .config import config
from .helpers import *

logger = logging.getLogger()

configuration = ""
user_cache = {}

connection = ""


def setup_ldap(config_dict):
    global configuration, connection
    configuration = config_dict
    if configuration.LDAP_IS_NTLM:
        connection = get_ntlm_connection()
    else:
        connection = get_ldap_connection()


def get_ldap_connection():
    """
    Creates a connection to the ldap-server provided in the config. Uses ldap3.
    :return: A ldap3 connection object.
    """
    logger.info("Establishing standard ldap connection")
    server = Server(configuration.LDAP_SERVER_URL, get_info=ALL, use_ssl=configuration.LDAP_USE_SSL,
                    port=configuration.LDAP_PORT)
    return Connection(server, configuration.LDAP_USER, configuration.LDAP_PASSWORD, auto_bind=True, read_only=True)


def get_ntlm_connection():
    """
    Creates a connection to a server using NTLM authentication. Uses ldap3
    :return: A ldap3 connection object with authentication set to NTLM.
    """
    logger.info("Establishing ntlm ldap connection")
    server = Server(configuration.LDAP_SERVER_URL, get_info=ALL, use_ssl=configuration.LDAP_USE_SSL,
                    port=configuration.LDAP_PORT)
    return Connection(server, user=configuration.LDAP_USER,
                      password=configuration.LDAP_PASSWORD, authentication=NTLM, read_only=True)


def fetch_users_of_group(group_name):
    """
    Searches all users of a specified group in the provided ldap-server. Returns the user objects as an array of
    dictionaries. Each dictionary resembles one user object containing the value "login".
    :param group: The LDAP-group the users should be searched in.
    :return: An array containing dictionaries each of which defines a user found in the provided group.
    """
    logger.info("Fetching users of ldap group %s " % group_name)
    result = []
    connection.bind()
    if configuration.LDAP_GROUP_SEARCH_FILTER:
        group_query_filter = "(&(cn=" + group_name + ")" + configuration.LDAP_GROUP_SEARCH_FILTER + ")"
    else:
        group_query_filter = "(cn=" + group_name + ")"
    groups = connection.extend.standard.paged_search(search_base=configuration.LDAP_GROUP_SEARCH_BASE,
                                                     search_filter=group_query_filter,
                                                     search_scope=SUBTREE,
                                                     attributes=[configuration.LDAP_MEMBER_ATTRIBUTE],
                                                     paged_size=5,
                                                     generator=True)
    for group in groups:
        for user in group["attributes"][configuration.LDAP_MEMBER_ATTRIBUTE]:
            if configuration.LDAP_USER_SEARCH_FILTER:
                user_query_filter = configuration.LDAP_USER_SEARCH_FILTER
            else:
                user_query_filter = "(objectClass=*)"
            logger.info("Fetching user %s of ldap group %s " % (user, group_name))
            user_data = connection.extend.standard.paged_search(search_base=user,
                                                                search_scope=SUBTREE,
                                                                search_filter=user_query_filter,
                                                                attributes=[configuration.LDAP_USER_LOGIN_ATTRIBUTE,
                                                                            configuration.LDAP_USER_NAME_ATTRIBUTE,
                                                                            configuration.LDAP_USER_MAIL_ATTRIBUTE],
                                                                paged_size=5)
            for user_set in user_data:
                data_set = user_set["attributes"]
                login = data_set[configuration.LDAP_USER_LOGIN_ATTRIBUTE]
                name = data_set[configuration.LDAP_USER_NAME_ATTRIBUTE]
                mail = data_set[configuration.LDAP_USER_MAIL_ATTRIBUTE]
                if not login or not name:
                    continue
                if not mail:
                    mail = login
                result.append({
                    "login": login if isinstance(login, str) else login[0],
                    "name": name if isinstance(name, str) else name[0],
                    "email": mail if isinstance(mail, str) else mail[0]
                })
    connection.unbind()
    return result


def get_users_of_group(group):
    """
    Returns all users found in the ldap group with the given name. If the group is already cached, the users are
    returned from the cache. Otherwise fetch_users_of_group is called with the group's name as parameter. The return
    value then is cached.
    :param group: The name of the group the users should be returned of.
    :return: A list containing dictionaries. Each dictionary consists of a login attribute and the respective user
    login.
    """
    if group not in user_cache:
        user_cache[group] = fetch_users_of_group(group)
    return user_cache[group]
