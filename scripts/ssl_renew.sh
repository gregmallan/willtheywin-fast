#!/bin/bash

COMPOSE="/usr/local/bin/docker-compose --no-ansi"
DOCKER="/usr/bin/docker"

cd /home/weatherapi/weather-api
$COMPOSE -f docker/prod/docker-compose-prod.yml run certbot renew && $DOCKER exec weatherapi_nginx_prod nginx -s reload
