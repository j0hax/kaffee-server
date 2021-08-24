# kaffee-server

[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/j0hax/kaffee-server.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/j0hax/kaffee-server/context:python)
[![Docker Image CI](https://github.com/j0hax/kaffee-server/actions/workflows/docker-image.yml/badge.svg)](https://github.com/j0hax/kaffee-server/actions/workflows/docker-image.yml)

REST-Schnittstelle für das [Kaffeesystem](https://github.com/j0hax/kaffee-ui)

⚠️ **Aktuell befindet sich der Server Code noch unter schwerer Entwickelung.** Große Änderungen sind bis zum Release 1.0 vorbehalten.

## Anwendungsbeispiel
[![asciicast](https://asciinema.org/a/422910.svg)](https://asciinema.org/a/422910)

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
