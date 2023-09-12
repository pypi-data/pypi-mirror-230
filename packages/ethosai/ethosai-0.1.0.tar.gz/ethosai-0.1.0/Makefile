activate = @. .venv/bin/activate;

setup:
	python3 -m venv .venv

build:
	rm -rf dist/
	$(activate) python3 -m pip install --upgrade build
	$(activate) python3 -m build

publish:
	$(activate) python3 -m twine upload dist/*
