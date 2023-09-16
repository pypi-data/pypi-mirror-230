#!/bin/sh

# source <script>

deactivate 2> /dev/null
rm -rf .venv docs
python -m venv .venv
source .venv/bin/activate
python -m pip install sphinx

#pip install -i https://test.pypi.org/simple/ vimbuilder
pip install vimbuilder

sphinx-build --version
sphinx-quickstart --sep -p Test -a TestAuthor -r 0.1 -l en docs
sed -e 's/extensions = \[\]/extensions = \["vimbuilder.builder"\]/' docs/source/conf.py > tempfile
mv tempfile docs/source/conf.py
# Edit Makefile
# sphinx-build -b vimhelp docs/source/ docs/build/vimhelp

