# kaffee-server

[![Python application](https://github.com/j0hax/kaffee-server/actions/workflows/python-app.yml/badge.svg)](https://github.com/j0hax/kaffee-server/actions/workflows/python-app.yml)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/j0hax/kaffee-server.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/j0hax/kaffee-server/context:python)

REST-Schnittstelle für das [Kaffeesystem](https://github.com/j0hax/kaffee-ui)

## Anwendungsbeispiel
```console
$ curl http://127.0.0.1/api
[
   {
      "balance":9001,
      "drinkCount":42,
      "hash":"9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
      "id":1,
      "lastUpdate":1617281972.4809017,
      "name":"Johannes Arnold"
   }
]
```

## Web-Oberfläche

![Überblick](screenshots/overview.png)
![Admin-Bereich](screenshots/admin.png)

Eine einfache Weboberfläche erlaubt für das Administrieren von Nutzerdaten.

## Datenbanken
### users
Die Users-Datenbank dient als Speicher für Nutzerdaten wie Name, Anzahl Buchungen, etc.

```console
$ sqlite3 -header -column coffee.db "SELECT * FROM users;"
name             balance     drink_count  last_update         transponder_hash                                                
---------------  ----------  -----------  ------------------  ----------------------------------------------------------------
Johannes Arnold  90001       42           1617281972.4809017  9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08
```

### clients
Die Clients-Datenbank enthält aktuell nur erlaubte API-Keys.

```console
$ sqlite3 -header -column coffee.db "SELECT * FROM clients;"
api_key                         
--------------------------------
pClZQgSXmHgIt1sHeOpb64iHrLxfc+7D
```

Neue API-Schlüssel können wie folgend mit zufälligen Daten erzeugt werden. 

```console
$ cat /dev/random | base64 | head -c 32
```
