test-pypi:
	python setup.py check
	rm -rf dist
	python setup.py sdist bdist_wheel
	twine upload -r testpypi dist/*

proj-doc:
	# python setup.py build_sphinx
	sphinx-apidoc -o docs/source mb_test_task
	$(MAKE) -C ./docs html

draft:
	# read release notes draft
	towncrier build --draft

release:
	@read -p "Enter final version as X.Y.Z:" bump; \
	python -m incremental.update mb_test_task --newversion=$$bump; \
	towncrier build --yes; \
	sphinx-apidoc -o docs/source mb_test_task; \
	$(MAKE) -C ./docs html; \
	git add .; \
	git status; \
	git commit -m "release $$bump"; \
	git tag "$$bump"; \
	git push origin --tags; \
	git push

test:
	python -m pytest -x -s -v -m "not slow"

check:
	echo "---> Check main package by flake8"; \
	flake8 mb_test_task; \
	echo "---> Check types annotation in main package"; \
	mypy mb_test_task; \
	echo "---> Check tests folder by flake8"; \
	flake8 tests

log:
	@read -p "Enter newsfragment name:" frag; \
	towncrier create $$frag

ipython:
	python -m IPython
