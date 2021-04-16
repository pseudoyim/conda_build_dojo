#!/bin/bash

cd /home/conda_build_dojo

pip install -e .

# As of 4/15/2021, also separately install python-tabulate from its master branch.
pip install git+https://github.com/astanin/python-tabulate.git@b2c26bcb70e497f674b38aa7e29de12c0123708a

exec bash