#!/bin/sh
set -x
export FLASK_APP=kaffee_server
export FLASK_ENV=development
flask run 