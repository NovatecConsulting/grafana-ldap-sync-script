from ldap3 import Server, Connection, ALL, SUBTREE

from .helpers import get_user_attr
from .config import config

configuration = ""


def get_ldap_connection():
    """
    Creates a connection to the ldap-server provided in the config. Uses ldap3.
    :return: A ldap3 connection object.
    """
    global configuration
    configuration = config()
    server = Server(configuration.LDAP_SERVER_URL, get_info=ALL)
    return Connection(server, configuration.LDAP_USER, configuration.LDAP_PASSWORD, auto_bind=True)


def get_users_of_group(group):
    """
    Searches all users of a specified group in the provided ldap-server. Returns the user objects as an array of
    dictionaries. Each dictionary resembles one user object with the values "name", "mail" and "login"
    :param group: The LDAP-group the users should be searched in.
    :return: An array containing dictionaries each of which defines a user found in the provided group.
    """
    result = []
    users = get_ldap_connection().extend.standard.paged_search(search_base=configuration.LDAP_USER_SEARCH_BASE,
                                                               search_filter="( "
                                                                             + configuration.LDAP_GROUP_DESCRIPTOR
                                                                             + "="
                                                                             + group
                                                                             + ")",
                                                               search_scope=SUBTREE,
                                                               attributes=["cn", "mail", "uid"],
                                                               paged_size=5,
                                                               generator=True)
    for user in users:
        result.append({"name": get_user_attr(user, "cn"), "mail": get_user_attr(user, "mail"),
                       "login": get_user_attr(user, "uid")})
    return result