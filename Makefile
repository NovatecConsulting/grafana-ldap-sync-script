init:
	pip install -r requirements.txt

bundle:
	rm grafana-ldap-sync-script.zip
	zip grafana-ldap-sync-script.zip \
		LICENSE \
		README.md \
		run.py \
		requirements.txt \
		config.yml \
		example.csv \
		script/* \
		-x 'script/__pycache__**'

test:
	nosetests tests
