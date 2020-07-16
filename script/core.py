import csv
import sys
import logging

from .grafana import *
from .ldap import *
from ldap3.core.exceptions import LDAPSocketOpenError
from requests.exceptions import ConnectionError
from .config import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("grafana-ldap-sync-script")

PERMISSION_MAP = {
    "View": 1,
    "Edit": 2,
    "Admin": 4
}

configuration = ""


def read_csv(file):
    """
    Reads the csv-file defined in CSV_FILE and returns it as a 2-dimensional array.
    :return: The given csv file parsed into a 2-dimensional array.
    """
    try:
        with open(file, newline='') as f:
            reader = csv.reader(f)
            data = list(reader)
    except FileNotFoundError as e:
        logger.error("Binding-file %s does not exist!", configuration.LDAP_BINDING_FILE)
    return data


def read_mapping_from_csv(bind):
    """
    Calls read_csv() and parses the loaded array into a dictionary. The dictionary is defined as follows:
    {
    "teams": {
        *team-name*: {
            "ldap": []
        },
        ....
      },
     "folders: {
        *folder-id*: {
            "name": *folder-name*,
            "permissions": [
            {
                "teamId": *team-name*,
                "permission0: *permission*"

            },
            ....
            ]
        },
        ...
    }
    :return: The csv's contents parsed into a dictionary as described above.
    """
    result = {"teams": {}, "folders": {}}
    csv_content = read_csv(bind)
    is_header = True
    for line in csv_content:
        if not is_header:
            ldap = line[0]
            team = line[1]
            folder_name = line[3]
            folder_uuid = line[4]
            permission = line[5]
            if not team in result["teams"]:
                result["teams"][team] = {"ldap": []}
            if not ldap in result["teams"][team]["ldap"]:
                result["teams"][team]["ldap"].append(ldap)
            if not folder_uuid in result["folders"]:
                result["folders"][folder_uuid] = {"name": folder_name, "permissions": []}
            access = {"teamId": team, "permission": permission}
            if not access in result["folders"][folder_uuid]["permissions"]:
                result["folders"][folder_uuid]["permissions"].append(access)
        else:
            is_header = False
    return result


def add_users(grafana_team, ldap_groups):
    """
    Takes the name of a grafana-team and a list of ldap groups. Returns an array of users which are part of the
    given ldap groups but not part of the given grafana-team.
    :param grafana_team: The name of the grafana-team the users should be added to.
    :param ldap_groups: The names of the ldap-groups the users should be added from.
    :return: An array containing all users that need to be added to the grafana-team.
    """
    grafana_users = get_members_of_team(grafana_team)
    for ldap_group in ldap_groups:
        ldap_users = get_users_of_group(ldap_group)
        for user in ldap_users:
            if user not in grafana_users:
                if not login_taken(user["login"]):
                    create_user_with_random_pw(user)
                add_user_to_team(user["login"], grafana_team)


def remove_users(grafana_team, ldap_groups):
    """
    Takes the name of a grafana-team and a list of ldap groups. Returns an array of users which are part of the given
    grafana-team but not of any of the given ldap-groups.
    :param grafana_team: The name of the grafana-team the users should be removed from.
    :param ldap_groups: The names of the ldap groups containing the users that should be present in the grafana-group.
    :return: An array containing all users that need to be removed from the grafana-team.
    """
    grafana_users = get_members_of_team(grafana_team)
    ldap_users = []
    for ldap_group in ldap_groups:
        users_of_group = get_users_of_group(ldap_group)
        for user in users_of_group:
            if user not in ldap_users:
                ldap_users.append(user)
    for user in grafana_users:
        if user not in ldap_users:
            try:
                remove_member_from_team(grafana_team, user["login"])
            except GrafanaClientError:
                break


def update_teams(team_mapping):
    """
    Creates a grafana team from a given team mapping if the team does not exist yet.
    A team mapping is a dictionary defined as follows:
    *team-name*: {
            "ldap": [
                    *mapped-ldap-group1*,
                    *mapped-ldap-group2*,
                    ]
    }
    Also all users of the provided LDAP-groups are added.
    :param team_mapping: A dictionary that resembles a team as described above.
    """
    for team in team_mapping:
        mapping = team_mapping[team]

        # Create team if it does not exist.
        if not get_id_of_team(team):
            create_team(team, "")

        # Add users to team, create account if necessary.
        add_users(team, mapping["ldap"])

        # Remove unwanted users from team.
        remove_users(team, mapping["ldap"])


def update_folders(folders):
    """
    Takes a dictionary resembling multiple folders and creates each folders with the provided name and uid.
    The dictionary should be defined as follows:
    {
    *folder-id1*: {
            "name": *folder-name*,
            "permissions": [
            {
                "teamId": *team-name*,
                "permission: *permission*"

            },
            ....
        },
    *folder-id2*:....
    }
    :param folders:
    """
    for folder_id in folders:
        if not exists_folder(folder_id):
            create_folder(folders[folder_id]["name"], folder_id)
        permissions = folders[folder_id]["permissions"]
        for permission in permissions:
            permission["teamId"] = get_id_of_team(permission["teamId"])
            permission["permission"] = PERMISSION_MAP[permission["permission"]]
        update_folder_permissions(folder_id, permissions)


def delete_unmapped_teams(team_mappings):
    """
    Deletes all teams which are not required anymore by the current mapping.
    :param team_mappings: The dictionary found under the name "team" in the mapping-dictionary.
    :return:
    """
    all_teams = get_all_teams()
    for team in all_teams:
        exists = False
        for team_name in team_mappings:
            if team["name"] == team_name:
                exists = True
        if not exists:
            delete_team_by_name(team["name"])


def get_users_of_used_ldap_groups(team_mappings):
    """
    Retrieves all users which are part of groups defined in the team mappings.
    :param team_mappings: The dictionary found under the name "team" in the mapping-dictionary.
    :return: A List of all users needed to be created in grafana.
    """
    users = []
    for team in team_mappings:
        for ldap_group in team_mappings[team]["ldap"]:
            for user in get_users_of_group(ldap_group):
                if not user in users:
                    users.append(user)
    return users


def delete_unmapped_users(team_mappings):
    """
    Deletes all users that are not needed by the current mapping.
    :param team_mappings: The dictionary found under the name "team" in the mapping-dictionar
    """
    grafana_users = get_all_users()
    ldap_users = get_users_of_used_ldap_groups(team_mappings)
    for user in grafana_users:
        exists = False
        for ldap_user in ldap_users:
            if ldap_user["login"] == user["login"]:
                exists = True
        if not exists:
            delete_user_by_login(user["login"])


def remove_unused_items(team_mappings):
    """
    Deletes all teams and user accounts which are not needed anymore.
    :param team_mappings: The dictionary found under the name "team" in the mapping-dictionary.
    """
    delete_unmapped_teams(team_mappings)
    delete_unmapped_users(team_mappings)


def export(config_path, bind, dry_run):
    """
    Checks if a .lock file is currently present. If no .lock file is present, the updating of the grafana teams,
    folders and users is performed.
    If a .lock file is present, no action is performed.
    """
    global configuration
    if lock():
        logger.info("Starting task...")
        try:
            configuration = config(config_path)
            configuration.DRY_RUN = dry_run
            if configuration.DRY_RUN:
                print("dryRun enabled: Changes will not be applied!")
            setup_grafana(configuration)
            setup_ldap(configuration)
            mapping = read_mapping_from_csv(bind)
            update_teams(mapping["teams"])
            update_folders(mapping["folders"])
            remove_unused_items(mapping["teams"])
            logger.info("Task finished successfully!")
        except LDAPSocketOpenError:
            logger.error("Task aborted, unable to reach LDAP-Server.")
        except ConnectionError:
            logger.error("Task aborted, unable to reach Grafana-Server.")
        except:
            logger.error("An unexpected error occured: %s", str(sys.exc_info()))
        unlock()
    else:
        logger.error("Task aborted, process is already active!")
