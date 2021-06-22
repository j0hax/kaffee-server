# kaffee-server

[![Python application](https://github.com/j0hax/kaffee-server/actions/workflows/python-app.yml/badge.svg)](https://github.com/j0hax/kaffee-server/actions/workflows/python-app.yml)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/j0hax/kaffee-server.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/j0hax/kaffee-server/context:python)
![Lines of code](https://img.shields.io/tokei/lines/github/j0hax/kaffee-server)

REST-Schnittstelle für das [Kaffeesystem](https://github.com/j0hax/kaffee-ui)

⚠️ **Aktuell befindet sich der Server Code noch unter schwerer Entwickelung.** Große Änderungen sind bis zum Release 1.0 vorbehalten.

## Anwendungsbeispiel
```console
$ curl http://server/api/
[
  {
    "balance": 200, 
    "depositCount": 1, 
    "deposits": 1000, 
    "id": 1, 
    "lastUpdate": 1624377216.0, 
    "name": "Buxe", 
    "transponder": "123", 
    "withdrawalCount": 20, 
    "withdrawals": -800
  }, 
  {
    "balance": 60, 
    "depositCount": 1, 
    "deposits": 500, 
    "id": 2, 
    "lastUpdate": 1624377219.0, 
    "name": "Johannes Arnold", 
    "transponder": "456", 
    "withdrawalCount": 11, 
    "withdrawals": -440
  }
]
```

## Web-Oberfläche

![Überblick](screenshots/overview.png)
![Admin-Bereich](screenshots/admin.png)

Eine einfache Weboberfläche erlaubt für das Administrieren von Nutzerdaten.

## Installation

Eine Unitdatei für Systemd ist unter [kaffee-server.service](/etc/systemd/system/kaffee-server.service) zu finden.

Es wird empfohlen einen HTTP-Server als Proxy zu benutzen (Apache, nginx) um auf Ports 80 und 443 auf den Server umzuleiten.

Neue API-Schlüssel können wie folgend mit zufälligen Daten erzeugt werden. 

```console
$ cat /dev/random | base64 | head -c 32
```
