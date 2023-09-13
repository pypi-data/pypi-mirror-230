#!/bin/bash

# create the virtual environment if one does not exist already
if [ ! -d "venv" ]; then
  virtualenv venv
fi

# activate the virtual environment
source venv/bin/activate

# install requirements from requirements.txt
pip install -r requirements.txt
pip install pytest

# run pytest
pytest

deactivate
