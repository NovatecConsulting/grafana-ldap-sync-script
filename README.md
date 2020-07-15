# grafana-ldap-sync-script
A script to get Grafana users, teams and their permissions from an LDAP server and keep it in sync.

## Installation
Install all dependencies
```bash
pip install -r requirements.txt
```

## Running the Script
The script can be simply run with:
```bash
python run.py
```

## Usage
If you just want to test the script, there is an example.csv predefined. Just enter your grafana credentials in the config.yml.
The used LDAP-Server can be found [here](https://www.forumsys.com/tutorials/integration-how-to/ldap/online-ldap-test-server/).

#### Config
Before starting the script you need to enter your grafana & ldap credentials in the config.yml. You also need to add the
path to your .csv file containing the bindings.

#### Binding
To bind LDAP-groups to grafana-teams and grant these teams access to folders you need to provide a .csv file. Please note 
that the first row of the csv is recognized as a header-row and is therefore being ignored. 
The file needs to contain the following information in this exact order: 
<br> 
```CSV
LDAP-Group, Grafana-Team Name, Grafana-Team ID, Grafana-Folder ID, Grafana-Folder UUID, Grafana-Folder Permission
```
Missing folders, teams and users will be created by the script.
<br>
Possible Grafana-Folder permissions are:
- View
- Edit 
- Admin

#### Removing Bindings
When a binding is removed in your .csv-file, this binding is also removed by the script. So if there is a team in your grafana instance which
is not defined by the current binding the team will be deleted. This also applies to users. **This does not apply to folders! 
Folders need to be deleted manually if not needed anymore!**