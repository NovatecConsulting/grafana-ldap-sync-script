import yaml


class config:

    def __init__(self):
        self.load_config()

    GRAFANA_AUTH = ""
    GRAFANA_URL = ""

    LDAP_SERVER_URL = ""
    LDAP_USER = ""
    LDAP_PASSWORD = ""
    LDAP_GROUP_SEARCH_BASE = ""
    LDAP_GROUP_DESCRIPTOR = ""
    LDAP_GROUP_SEARCH_FILTER = ""
    LDAP_MEMBER_ATTRIBUTE = ""
    LDAP_USER_LOGIN_ATTRIBUTE = ""
    LDAP_IS_NTLM = False
    CSV_FILE = ""

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
        self.LDAP_GROUP_SEARCH_BASE = config["ldap"]["searchBase"]
        self.LDAP_GROUP_SEARCH_FILTER = config["ldap"]["groupSearchFilter"]
        self.LDAP_GROUP_DESCRIPTOR = config["ldap"]["groupDescriptor"]
        self.LDAP_MEMBER_ATTRIBUTE = config["ldap"]["memberAttributeName"]
        self.LDAP_USER_LOGIN_ATTRIBUTE = config["ldap"]["userLoginAttribute"]
        self.LDAP_IS_NTLM = config["ldap"]["useNTML"]
        self.CSV_FILE = config["csvPath"]
