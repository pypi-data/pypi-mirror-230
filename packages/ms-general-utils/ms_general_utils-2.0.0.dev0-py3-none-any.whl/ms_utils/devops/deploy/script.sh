#!/bin/sh
# shellcheck disable=SC2046
# shellcheck disable=SC2002
export $(grep -v '^#' .env | xargs -d '\r')
flask db upgrade
gunicorn 'app:create_app()' -w 2 --threads 2 -b 0.0.0.0:$1