#!/usr/bin/env bash

# Check if a virtual environment exists
if [ ! -f venv/bin/python ]; then
    python3 -m venv venv
fi

source venv/bin/activate

# install pre-commit
pip install pre-commit

# install hooks
pre-commit install --install-hooks --overwrite
