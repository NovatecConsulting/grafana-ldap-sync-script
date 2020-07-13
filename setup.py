from setuptools import setup, find_packages


setup(
    name='grafana-ldap-syn-script',
    version='0.1.0',
    description='Script for syncing LDAP Users & Groups with Grafana Users & Teams',
    packages=find_packages(exclude=('tests', 'docs'))
)

