#!/bin/bash

COMPOSE="/usr/local/bin/docker-compose --no-ansi"
DOCKER="/usr/bin/docker"

cd /home/willtheywin-fast/willtheywin-fast
$COMPOSE -f docker-compose-prod.yml run certbot renew && $DOCKER exec willtheywinfast_nginx_prod nginx -s reload
