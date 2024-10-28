from setuptools import find_packages, setup

setup(
    name='script',
    version='1.1.0',
    description='Script for syncing LDAP Users & Groups with Grafana Users & Teams',
    packages=find_packages(exclude=('tests', 'docs')),
    package_data={'grafana-ldap-syn-script': ['run.py']},
    include_package_data=True,
    install_requires=[
        "requests>=2.24.0",
        "grafana_api",
        "ldap3>=2.7",
        "mock>=4.0.2",
        "PyYAML>=5.3.1",
        "setuptools>=9.2.0",
        "pyasn1>=0.4.6"]
)

