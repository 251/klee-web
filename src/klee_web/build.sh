#!/bin/bash

set -e

CUR_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

echo "Running flake8"
flake8 --extend-ignore=E722,E501 --max-complexity 12 --exclude=migrations "${CUR_DIR}"

npm install
bower install --config.interactive=false --allow-root
grunt
python manage.py collectstatic --noinput
