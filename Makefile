DOCKER_REPO ?= DOCKERHUB_USER/grafana-ldap-sync-script
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

docker-run: docker-build
	docker run --mount 'type=bind,source=${PWD},target=/data' ${DOCKER_REPO}:${DOCKER_TAG} --config /data/config.yml --bind /data/example.csv

docker-explore: docker-build
	docker run -it --entrypoint /bin/bash --mount 'type=bind,source=${PWD},target=/data' ${DOCKER_REPO}:${DOCKER_TAG} -o vi
