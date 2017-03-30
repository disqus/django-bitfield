develop:
	@echo "--> Installing dependencies"
	pip install -e .
	pip install "file://`pwd`#egg=django-bitfield[tests]"
	@echo ""

test:
	@echo "--> Running Python tests"
	tox
	@echo ""

lint:
	@echo "--> Linting Python files"
	PYFLAKES_NODOCTEST=1 flake8 bitfield
	@echo ""


publish:
	python setup.py sdist bdist_wheel upload

.PHONY: test publish
