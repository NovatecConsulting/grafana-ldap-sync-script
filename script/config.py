import yaml
import os

path = os.getcwd() + "\\export-script"


class config:

    def __init__(self):
        self.load_config()

    GRAFANA_AUTH = ""
    GRAFANA_URL = ""

    LDAP_SERVER_URL = ""
    LDAP_USER = ""
    LDAP_PASSWORD = ""
    LDAP_USER_SEARCH_BASE = ""
    LDAP_GROUP_DESCRIPTOR = "ou"
    LDAP_GROUP_SEARCH_FILTER = ""

    CSV_FILE = "./test.csv"

    def load_config(self):
        """
        Loads the config.yml file present in the directory and fills all global variables with the defined config.
        """
        config = yaml.safe_load(open('./config.yml'))["config"]
        self.GRAFANA_AUTH = (
            config["grafana"]["user"],
            config["grafana"]["password"]
        )
        self.GRAFANA_URL = config["grafana"]["url"]

        self.LDAP_SERVER_URL = config["ldap"]["url"]
        self.LDAP_USER = config["ldap"]["login"]
        self.LDAP_PASSWORD = config["ldap"]["password"]
        self.LDAP_USER_SEARCH_BASE = config["ldap"]["baseDB"]
        self.LDAP_GROUP_SEARCH_FILTER = config["ldap"]["groupSearchFilter"]
        self.LDAP_GROUP_DESCRIPTOR = config["ldap"]["groupDescriptor"]
