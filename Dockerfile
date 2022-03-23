FROM python:3-slim

WORKDIR /usr/src/app

RUN apt-get update -y && apt-get -y install locales build-essential libev-dev && \
    sed -i -e "s/# de_DE.UTF-8 UTF-8/de_DE.UTF-8 UTF-8/" /etc/locale.gen && \
    locale-gen

ENV TZ="Europe/Berlin"

RUN pip install poetry

COPY . .

RUN [ "poetry", "install", "--no-dev" ]

# Initialize the database
ENV FLASK_APP="kaffee_server"
RUN ["poetry", "run", "flask", "init-db" ]

# Run WSGI
EXPOSE 5000
ENTRYPOINT [ "poetry", "run", "python", "wsgi.py" ]
