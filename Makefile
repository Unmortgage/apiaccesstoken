#
PACKAGE=apiaccesstoken
# actual package imported
IMPORT=apiaccesstoken
VERSION=$(shell cat VERSION)
BIN=${VIRTUALENV}/bin
DOCKER_NAME=${PACKAGE}
DOCKER_VERSION=${VERSION}
DOCKER_IMAGE=${DOCKER_NAME}:${DOCKER_VERSION}
export TWINE_USERNAME=jenkins
export TWINE_REPOSITORY_URL=http://pypi.evasionproject.com/simple

clean:
	find . -iname '*.pyc' -exec rm {} \; -print

install:
	python setup.py develop

test_install: install
	pip install -r test-requirements.txt

test: test_install
	pytest --junitxml=tests/report.xml --cov=${IMPORT}

release:
	rm -f dist/*
	pip install -r build-requirements.txt
	python setup.py sdist bdist_wheel
	twine upload dist/*

tag:
	# won't work inside docker box, jenkins after release will tag and
	# announce this.
	git tag ${VERSION}
	git push --tags


docker_build:
	docker build -t ${DOCKER_IMAGE} .

docker_rebuild:
	docker build \
		--no-cache \
		-t ${DOCKER_IMAGE} .

docker_test: clean docker_build
	# Run the tests with coverage report. Using a volume mount, recover the
	# coverage report from the container and put it in the hosts tests
	# directory. The Jenkinsfile junit section and then recover the file.
	docker run -u 0  -v $(shell pwd):/src ${DOCKER_IMAGE} \
		bash -c 'make test ; cp /app/tests/report.xml /src/tests/'

docker_release:
	docker run \
		-e TWINE_REPOSITORY_URL=${TWINE_REPOSITORY_URL} \
		-e TWINE_USERNAME=${TWINE_USERNAME} \
		-e TWINE_PASSWORD=${TWINE_PASSWORD} \
		${DOCKER_IMAGE} make release

docker_shell:
	docker run -u 0 -it ${DOCKER_IMAGE} bash
