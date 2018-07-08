#
PACKAGE=apiaccesstoken
# actual package imported
IMPORT=apiaccesstoken
BIN=${VIRTUALENV}/bin
DOCKER_NAME=${PACKAGE}
export VERSION=$(shell cat ./VERSION)
export TWINE_USERNAME=jenkins
export PYPI_HOST=pypi.evasionproject.com
export TWINE_REPOSITORY_URL=http://${PYPI_HOST}/simple
# If TWINE_PASSWORD is defined this is running under jenkins build and
# dependancies are to come from out internal PYPI:
ifdef TWINE_PASSWORD
PIP_INSTALL=pip install \
	--trusted-host ${PYPI_HOST} \
	-i http://${TWINE_USERNAME}:${TWINE_PASSWORD}@${PYPI_HOST}/simple \
	-r requirements.txt
PIP_INSTALL_CMD=${PIP_INSTALL} --no-cache-dir -r requirements.txt
PIP_INSTALL_TEST_CMD=${PIP_INSTALL} --no-cache-dir -r test-requirements.txt
else
# Assume running in dev and depeancies are set up in the env:
PIP_INSTALL_CMD=pip install --no-cache-dir -r requirements.txt
PIP_INSTALL_TEST_CMD=pip install --no-cache-dir -r test-requirements.txt
endif

clean:
	rm -rf dist/ build/
	find . -iname '*.pyc' -exec rm {} \; -print

install:
	${PIP_INSTALL_CMD}
	python setup.py develop

test_install: install
	${PIP_INSTALL_TEST_CMD}

test: test_install
	pytest --junitxml=tests/report.xml \
		--cov=${IMPORT}  \
		--cov-report=term \
		--cov-report=html

build: clean
	pip install -r build-requirements.txt
	python setup.py sdist

release: build
	twine upload dist/*

docker_build:
	docker build \
		--build-arg TWINE_PASSWORD=${TWINE_PASSWORD} \
		-t ${DOCKER_NAME}:${VERSION} .

docker_rebuild:
	docker build \
		--no-cache \
		--build-arg TWINE_PASSWORD=${TWINE_PASSWORD} \
		-t ${DOCKER_NAME}:${VERSION} .

docker_test: clean docker_build
	# Run the tests with coverage report. Using a volume mount, recover the
	# coverage report from the container and put it in the hosts tests
	# directory. The Jenkinsfile junit section and then recover the file.
	docker run \
		-u 0 \
		-e TWINE_REPOSITORY_URL=${TWINE_REPOSITORY_URL} \
		-e TWINE_USERNAME=${TWINE_USERNAME} \
		-e TWINE_PASSWORD=${TWINE_PASSWORD} \
		-v $(shell pwd):/src \
		${DOCKER_NAME}:${VERSION} \
		bash -c 'make test ; \
			cp /app/tests/report.xml /src/tests/ ; \
			cp -a /app/htmlcov /src/ '

docker_release:
	docker run \
		-u 0 \
		-e TWINE_REPOSITORY_URL=${TWINE_REPOSITORY_URL} \
		-e TWINE_USERNAME=${TWINE_USERNAME} \
		-e TWINE_PASSWORD=${TWINE_PASSWORD} \
		${DOCKER_NAME}:${VERSION} make release

docker_shell:
	docker run \
		-u 0 \
		-it \
		-e TWINE_REPOSITORY_URL=${TWINE_REPOSITORY_URL} \
		-e TWINE_USERNAME=${TWINE_USERNAME} \
		-e TWINE_PASSWORD=${TWINE_PASSWORD} \
		${DOCKER_NAME}:${VERSION} \
		/bin/bash
