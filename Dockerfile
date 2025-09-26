FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    apache2 libapache2-mod-wsgi-py3 python3 python3-pip openssl sqlite3 \
    && pip3 install flask

# Enable SSL and WSGI
RUN a2enmod ssl wsgi headers

# Copy app and config
COPY app/ /var/www/app/
COPY apache/app.conf /etc/apache2/sites-available/app.conf
RUN a2ensite app.conf

# TODO: I think this is poorly implemented
# Generate CA and server certs
RUN mkdir -p /etc/ssl/ca /etc/ssl/server /data \
 && openssl genrsa -out /etc/ssl/ca/ca.key.pem 4096 \
 && openssl req -x509 -new -nodes -key /etc/ssl/ca/ca.key.pem \
      -days 3650 -subj "/CN=BookmarkSearch CA" \
      -out /etc/ssl/ca/ca.crt.pem \
 && openssl genrsa -out /etc/ssl/server/server.key.pem 2048 \
 && openssl req -new -key /etc/ssl/server/server.key.pem \
      -subj "/CN=localhost" \
      -out /etc/ssl/server/server.csr.pem \
 && openssl x509 -req -in /etc/ssl/server/server.csr.pem \
      -CA /etc/ssl/ca/ca.crt.pem -CAkey /etc/ssl/ca/ca.key.pem \
      -CAcreateserial -days 365 \
      -out /etc/ssl/server/server.crt.pem

EXPOSE 443
CMD ["apachectl", "-D", "FOREGROUND"]
