PROJECT = railgun

## Testing
test: cog
	tox

inplace-test: cog build-inplace test-ext
	nosetests --with-doctest --with-xunit railgun tests

build-inplace:
	python setup.py build_ext -i

test-ext:
	make --directory=tests/ext/

clean: clean-pycache
	rm -rf *.egg-info .tox MANIFEST

clean-pycache:
	find $(PROJECT) -name __pycache__ -o -name '*.pyc' -print0 \
		| xargs --null rm -rf

## Update files using cog.py
cog: $(PROJECT)/__init__.py
$(PROJECT)/__init__.py: README.rst
	cd $(PROJECT) && cog.py -r __init__.py

## Upload to PyPI
upload: cog
	python setup.py register sdist upload
