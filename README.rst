===============
 Kaffee Server
===============

.. image:: https://img.shields.io/docker/image-size/j0hax/kaffee-server   :alt: Docker Image Size (latest by date)

Features
==========

- Einfache Verwaltung von mehreren Nutzern
- Kommunikation mit beliebigen Buchungs-Terminals
- REST-Schnittstelle für das einfache Parsen von Statistiken
- BWL-Wörter wie *Saldo* und *Soll-Haben*

Installation
============

Mit Docker (empfohlen)
----------------------

1. Docker und docker-compose installieren
2. Repo klonen
3. :code:`docker-compose up -d` ausführen

Direkt
------

1. Python und Poetry_ installieren
2. Repo klonen
3. :code:`poetry run flask init-db` ausführen, um die Datenbank zu initialisieren
4. :code:`poetry run python wsgi.py` ausführen, um den Server auszuführen

.. _Poetry: https://python-poetry.org/docs/#installation
