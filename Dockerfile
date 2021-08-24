FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Install and set locales
RUN apt-get update
RUN apt-get install -y locales locales-all

ENV LC_ALL de_DE.UTF-8

ENV FLASK_APP="kaffee_server"
ENV FLASK_ENV="development"

EXPOSE 5000

RUN flask init-db

ENTRYPOINT [ "flask" ]

CMD [ "run", "-h", "0.0.0.0" ]
