# kaffee-server

[![Python application](https://github.com/j0hax/kaffee-server/actions/workflows/python-app.yml/badge.svg)](https://github.com/j0hax/kaffee-server/actions/workflows/python-app.yml)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/j0hax/kaffee-server.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/j0hax/kaffee-server/context:python)

REST-Schnittstelle für das Kaffeesystem

## Anwendungsbeispiel
```console
$ curl 127.0.0.1:5000/api
[
  {
    "balance": 9000, 
    "drinkCount": 30, 
    "hash": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08", 
    "id": 1, 
    "lastUpdate": 1616751016000, 
    "name": "Johannes Arnold"
  }
]
```
