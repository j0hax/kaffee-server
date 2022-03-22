FROM python:3-slim

WORKDIR /usr/src/app

# Install and set locales and dependencies
RUN apt-get update
RUN apt-get install -y locales locales-all curl libev-dev gcc sqlite3

ENV LC_ALL="de_DE.UTF-8"
ENV TZ="Europe/Berlin"

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:${PATH}"

COPY . .

RUN [ "poetry", "install", "--no-dev" ]

# Initialize the database
ENV FLASK_APP="kaffee_server"
RUN ["poetry", "run", "flask", "init-db" ]

# Run WSGI
EXPOSE 5000
ENTRYPOINT [ "poetry", "run", "python", "wsgi.py" ]
