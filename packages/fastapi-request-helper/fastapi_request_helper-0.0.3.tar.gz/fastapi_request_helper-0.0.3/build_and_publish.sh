#!/usr/bin/env sh

rm -rf dist/

python3 -m pip install --upgrade build
python3 -m build

python3 -m pip install --upgrade twine
chmod 600 .pypirc
python3 -m twine upload dist/*

