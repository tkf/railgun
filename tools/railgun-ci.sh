#!/bin/sh

python setup.py build_ext -i
make --directory=tests/ext/
nosetests tests --with-xunit
export PYTHONPATH="`pwd`:$PYTHONPATH"
echo "PYTHONPATH=$PYTHONPATH"
cd doc/ && make clean && make html
