FROM python:3

WORKDIR /usr/src/app

# Install and set locales and libev
RUN apt-get update
RUN apt-get install -y locales locales-all libev-dev

ENV LC_ALL="de_DE.UTF-8"
ENV TZ="Europe/Berlin"

# Install python requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Initialize the database
ENV FLASK_APP="kaffee_server"
RUN flask init-db

# Run WSGI
EXPOSE 5000
ENTRYPOINT [ "python3" ]
CMD [ "wsgi.py" ]
