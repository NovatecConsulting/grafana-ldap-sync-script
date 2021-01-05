DOCKER_REPO ?= bushelpowered/grafana-ldap-sync-script
DOCKER_TAG ?= v1.0

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

docker-build:
	docker build -t ${DOCKER_REPO}:latest .
	docker tag ${DOCKER_REPO}:latest ${DOCKER_REPO}:${DOCKER_TAG}

docker-push: docker-build
	docker push ${DOCKER_REPO}:latest
	docker push ${DOCKER_REPO}:${DOCKER_TAG}
