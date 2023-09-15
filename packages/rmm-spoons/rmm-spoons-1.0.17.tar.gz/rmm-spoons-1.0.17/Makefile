.PHONY: install, package, upload, clean, venv, dist_clean, install_user

clean:
	rm -rf dist/* ; \
	rm -rf .venv; \
	find -iname "*.pyc" -delete

dist_clean:
	rm -rf dist/* ;

package: venv
	pip install build ; \
	python3 -m build ;

upload: venv dist_clean package
	pip install twine ; \
	python3 -m twine upload dist/*

upload_test: venv dist_clean package
	pip install twine ; \
	python3 -m twine upload --repository testpypi dist/*

install: venv
	python3 -m pip install .

install_user:
	python3 -m pip -u install .

venv:
	test -d .venv || python -m venv .venv; \
	source .venv/bin/activate;
