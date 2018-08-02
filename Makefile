check: mypy flake8 pylint

mypy:
	MYPYPATH=stubs mypy --strict fxwebgen

flake8:
	flake8 fxwebgen

pylint:
	pylint --rcfile .pylintrc fxwebgen

push: check
	git push && git push --tags

