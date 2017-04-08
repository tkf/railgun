PROJECT = railgun

## Testing
test: inject-readme
	tox

inplace-test: inplace-test-py27 inplace-test-py36

inplace-test-py27 inplace-test-py36: \
inplace-test-%: inject-readme test-ext
	.tox/$*/bin/pip install --editable .
	.tox/$*/bin/py.test src/railgun tests

test-ext:
	make --directory=tests/ext/

clean: clean-pycache
	rm -rf src/*.egg-info .tox MANIFEST

clean-pycache:
	find src tests -name __pycache__ -o -name '*.pyc' -print0 \
		| xargs --null rm -rf

## inject README contents to __init__.py
inject-readme: src/$(PROJECT)/__init__.py
src/$(PROJECT)/__init__.py: README.rst
	sed '1,/^"""$$/d' $@ > $@.tail
	rm $@
	echo '"""' >> $@
	cat README.rst >> $@
	echo '"""' >> $@
	cat $@.tail >> $@
	rm $@.tail
# Note that sed '1,/^"""$/d' prints the lines after the SECOND """
# because the first """ appears at the first line.

## Upload to PyPI
upload: inject-readme
	rm -rf dist/
	python setup.py sdist
	twine upload dist/*
