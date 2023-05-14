#!/bin/sh

python3 -m flask db upgrade
python3 -m flask create-config
python3 -m flask create-template
python3 /app/metatube.py