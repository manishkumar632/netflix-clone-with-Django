#!/bin/bash
python3 manage.py collectstatic --noinput
python3 -m pip install requirements.txt