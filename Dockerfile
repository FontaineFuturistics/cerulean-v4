FROM php:8.1-apache

# Install dependencies
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
     openssl sqlite3 libsqlite3-dev \
  && docker-php-ext-install pdo_sqlite \
  && a2enmod ssl headers \
  && rm -rf /var/lib/apt/lists/*

# Copy Apache SSL vhost
COPY default-ssl.conf /etc/apache2/sites-available/default-ssl.conf
RUN a2ensite default-ssl

# Generate CA and server certificates
RUN mkdir -p /etc/ssl/ca /etc/ssl/private /etc/ssl/server \
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

# Copy application code
COPY html/ /var/www/html/
RUN chown -R www-data:www-data /var/www/html

# Expose HTTPS port and launch
EXPOSE 443
CMD ["apache2-foreground"]
