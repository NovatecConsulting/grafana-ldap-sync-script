# Grafana-LDAP-SYNC-SCRIPT

## Usage

[Helm](https://helm.sh) must be installed to use the charts.  Please refer to
Helm's [documentation](https://helm.sh/docs) to get started.

Once Helm has been set up correctly, add the repo as follows:

    helm repo add grafana-ldap-sync-script novatecconsulting.github.io/grafana-ldap-sync-script

If you had already added this repo earlier, run `helm repo update` to retrieve
the latest versions of the packages.  You can then run `helm search repo
{alias}` to see the charts.

To install the grafana-ldap-sync-script chart:

    helm install grafana-ldap-sync grafana-ldap-sync-script/grafana-ldap-sync

To uninstall the chart:

    helm delete grafana-ldap-sync