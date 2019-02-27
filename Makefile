
deps:
	pipenv install --dev

test: mamba behave

behave:
	pipenv run behave --tags=-skip test/e2e 

mamba:
	pipenv run mamba test

pep8:
	pipenv run pycodestyle genyrator

bookshop-build:
	pipenv run python bookshop.py


deploy: deploy-clean deploy-build deploy-deploy


deploy-clean:
	rm -rf build/ dist/ genyrator.egg-info/

deploy-build:
	pipenv run python setup.py sdist bdist_wheel

deploy-deploy:
	pipenv run twine upload --repository-url https://test.pypi.org/legacy/ dist/*

.PHONY: deps test behave pep8 bookshop-build
