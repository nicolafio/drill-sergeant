#!/bin/bash

cd "$(dirname $0)"

. .venv/bin/activate
python3 -m flask run
