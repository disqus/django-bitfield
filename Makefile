test:
	python setup.py test

publish:
	python setup.py sdist bdist_wheel upload

.PHONY: test publish
