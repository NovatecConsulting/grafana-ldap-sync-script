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

#### Config
Before starting the script, you need to enter your grafana & ldap credentials in the config.yml file.

#### Binding
To bind LDAP-Groups to Grafana-Teams and grant these teams access to folders, you need to provide a csv-file. Please note, that the first row of the csv is 
recognized as a header-row and is therefore being ignored. 
The file needs to contain the following information in this exact order: 
<br> 
LDAP-Group, Grafana-Team Name, Grafana-Team ID, Grafana-Folder ID, Grafana-Folder UUID, Grafana-Folder Permission
<br>
<br>
Possible permissions are:
- View
- Edit 
- Admin

#### Removing Bindings
When a binding is removed in your .csv-file, this binding is also removed by the script. So if there is a team in your grafana instance which
is not defined by the current binding the team will be deleted. This also applies to users. **This does not apply to folders! 
Folders need to be deleted manually if not needed anymore!**