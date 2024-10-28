# grafana-ldap-sync-script
A script to get Grafana users, teams and their permissions from an LDAP server and keep it in sync.

## Installation
Install all dependencies.
```bash
pip install -r requirements.txt
```

or consider to install the dependencies only for the user which will be executing the script:

```bash
$ pip install --user -r requirements.txt
```

## Running the Script

*The script requires Python 3 to run!*

It can be simply run with:
```bash
$ python run.py [-h] --config <path-to-config.yml> --bind <path-to-bind-csv> [--dry-run]
```

## Usage
If you just want to test the script, there is an example.csv predefined. Just enter your grafana credentials in the config.yml.
The used LDAP-Server can be found [here](https://www.forumsys.com/tutorials/integration-how-to/ldap/online-ldap-test-server/).

### Config
Before starting the script you need to enter your grafana & ldap credentials in the config.yml. You also need to add the
path to your .csv file containing the bindings.

### Binding
To bind LDAP-groups to grafana-teams and grant these teams access to folders you need to provide a .csv file. Please note
that the first row of the csv is recognized as a header-row and is therefore being ignored.
The file needs to contain the following information in this exact order:
* **LDAP-Group**: The LDAP group which will be used for mapping.
* **Grafana-Team Name**: The name of the Grafana team which will be created (if not exist) and where the group's users will be added to.
* **Grafana-Team ID**: The ID of the Grafana team (currently not used).
* **Grafana-Folder Name**: The Grafana folder which will be created (if not exist) and where the group's users will have the specified permission to.
* **Grafana-Folder UUID**: The UUID of the Grafana folder.
* **Grafana-Folder Permission**: The users' permission for the specified Grafana folder. (`View`, `Edit`, `Admin`)

Missing folders, teams and users will be created by the script.
Teams and users which are not existing in the LDAP mapping will be removed. Note: the user used by the script will not be deleted!

#### Example CSV
```CSV
ZBV/LDAP-Gruppe,Grafana-Team-Name,Grafana-Team-ID,Grafana-Folder-Name,Grafana-Folder-UUID,Grafana-Folder-Permissions
mathematicians,mathematicians,0,Math,math_folder,Admin
mathematicians,smart_people,0,Common Dashboards,all_folder,View
scientists,scientists,0,Science,science_folder,Edit
scientists,smart_people,0,Common Dashboards,all_folder,View
```

Using this CSV mapping will result in the following operations:
* The Grafana teams `mathematicians`, `smart_people` and `scientists` will be created.
* The Grafana folders `Math`, `Common Dashboards` and `Science` will be created.
* All users in the `mathematicians` LDAP group will be member of the Grafana team `mathematicians` and `smart_people`.
* All users in the `scientists` LDAP group will be member of the Grafana team `scientists`.
* All users in the `mathematicians` LDAP group will get `Admin` access to the `Math` folder.
* All users in the `mathematicians` LDAP group will get `View` access to the `Common Dashboards` folder.
* All users in the `scientists` LDAP group will get `Edit` access to the `Science` folder.
* All users in the `scientists` LDAP group will get `View` access to the `Common Dashboards` folder.

#### Removing Bindings
When a binding is removed in your .csv-file, this binding is also removed by the script. So if there is a team in your grafana instance which
is not defined by the current binding the team will be deleted. This also applies to users. **This does not apply to folders!
Folders need to be deleted manually if not needed anymore!**


## Bundle Scripts

Using the Makefile, you can bundle all the scripts into a single zip-archive.

```
$ make bundle
```