import logging

import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("grafana-ldap-sync-script")

class config:

    def __init__(self):
        self.load_config("")

    def __init__(self, config_path):
        self.load_config(config_path)

    GRAFANA_AUTH = ""
    GRAFANA_URL = ""
    GRAFANA_PROTOCOL = "http"
    GRAFANA_ORG_ID = None

    LDAP_SERVER_URL = ""
    LDAP_PORT = ""
    LDAP_USER = ""
    LDAP_PASSWORD = ""
    LDAP_GROUP_SEARCH_BASE = ""
    LDAP_GROUP_DESCRIPTOR = ""
    LDAP_GROUP_SEARCH_FILTER = ""
    LDAP_SEARCH_RECURSIVELY = False
    LDAP_MEMBER_ATTRIBUTE = ""
    LDAP_IS_NTLM = False
    LDAP_USE_SSL = False
    LDAP_USER_LOGIN_ATTRIBUTE = ""
    LDAP_USER_NAME_ATTRIBUTE = ""
    LDAP_USER_MAIL_ATTRIBUTE = ""
    LDAP_USER_SEARCH_BASE = ""
    LDAP_USER_SEARCH_FILTER = ""

    DRY_RUN = False

    def load_config(self, config_path):
        """
        Loads the config_mock.yml file present in the directory and fills all global variables with the defined config.
        """
        try:
            with open(config_path) as f:
                config = yaml.safe_load(f)["config"]
        except FileNotFoundError as e:
            logger.error("Config file %s does not exist!", config_path)
            raise e
        except Exception as e:
            logger.error("Error reading config file %s: %s", config_path, str(e))

        grafana_config = config.get("grafana", {})
        self.GRAFANA_AUTH = (
            grafana_config.get("user", ""),
            grafana_config.get("password", "")
        )
        self.GRAFANA_URL = grafana_config.get("url", self.GRAFANA_URL)
        self.GRAFANA_PROTOCOL = grafana_config.get("protocol", self.GRAFANA_PROTOCOL)
        self.GRAFANA_ORG_ID = config["grafana"]["org_id"] if "org_id" in config["grafana"] else None

        ldap_config = config.get("ldap", {})

        self.LDAP_SERVER_URL = ldap_config.get("url", self.LDAP_SERVER_URL)
        self.LDAP_PORT = ldap_config.get("port", self.LDAP_PORT)
        self.LDAP_USER = ldap_config.get("login", self.LDAP_USER)
        self.LDAP_PASSWORD = ldap_config.get("password", self.LDAP_PASSWORD)
        self.LDAP_GROUP_SEARCH_BASE = ldap_config.get("groupSearchBase", self.LDAP_GROUP_SEARCH_BASE)
        self.LDAP_GROUP_SEARCH_FILTER = ldap_config.get("groupSearchFilter", self.LDAP_GROUP_SEARCH_FILTER)
        self.LDAP_MEMBER_ATTRIBUTE = ldap_config.get("memberAttributeName", self.LDAP_MEMBER_ATTRIBUTE)
        self.LDAP_USER_LOGIN_ATTRIBUTE = ldap_config.get("userLoginAttribute", self.LDAP_USER_LOGIN_ATTRIBUTE)
        self.LDAP_IS_NTLM = ldap_config.get("useNTLM", self.LDAP_IS_NTLM)
        self.LDAP_USE_SSL = ldap_config.get("useSSL", self.LDAP_USE_SSL)
        self.LDAP_USER_LOGIN_ATTRIBUTE = ldap_config.get("userLoginAttribute", self.LDAP_USER_LOGIN_ATTRIBUTE)
        self.LDAP_USER_NAME_ATTRIBUTE = ldap_config.get("userNameAttribute", self.LDAP_USER_NAME_ATTRIBUTE)
        self.LDAP_USER_MAIL_ATTRIBUTE = ldap_config.get("userMailAttribute", self.LDAP_USER_MAIL_ATTRIBUTE)
        self.LDAP_USER_SEARCH_BASE = ldap_config.get("userSearchBase", self.LDAP_USER_SEARCH_BASE)
        self.LDAP_USER_SEARCH_FILTER = ldap_config.get("userSearchFilter", self.LDAP_USER_SEARCH_FILTER)
        self.LDAP_SEARCH_RECURSIVELY = ldap_config.get("searchRecursively", self.LDAP_SEARCH_RECURSIVELY)
