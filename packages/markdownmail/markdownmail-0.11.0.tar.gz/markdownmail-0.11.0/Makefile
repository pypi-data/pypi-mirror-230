BIN_DIR = .tox/py39/bin/
VIRTUALENV_PATH = local.virtualenv

continuous-integration: install test

install:
	rm -rf ${VIRTUALENV_PATH}
	virtualenv -p python3.9 ${VIRTUALENV_PATH}
	${VIRTUALENV_PATH}/bin/pip install --requirement requirements.txt
	${VIRTUALENV_PATH}/bin/tox --recreate --notest

test:
	${VIRTUALENV_PATH}/bin/tox

watchtest:
	${VIRTUALENV_PATH}/bin/ptw

clean:
	rm -rf dist *.egg-info .tox .eggs README.html
	find . -name *.pyc -delete
	find . -type d -name "__pycache__" -delete

package:
	$(BIN_DIR)pip install wheel
	$(BIN_DIR)python setup.py sdist bdist_wheel

upload:
	$(BIN_DIR)pip install twine
	@echo "Run the effective command:"
	#.tox/py39/bin/twine upload dist/* --verbose --username USERNAME --password PASSWORD

shell:
	@echo "\t\`make check\` must be executed before (at least one time)."
	@$(BIN_DIR)python
