
deps:
	pipenv install --dev

test: pep8 mamba behave

behave:
	pipenv run behave --tags=-skip test/e2e 

mamba:
	pipenv run mamba test

pep8:
	pipenv run pycodestyle

bookshop-build:
	pipenv run python bookshop.py


deploy:
	bash deploy.sh

.PHONY: deps test behave pep8 bookshop-build
