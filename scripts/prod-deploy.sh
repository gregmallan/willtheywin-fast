#!/usr/bin/env bash

set -e

echo " -- Deploying willtheywin-fast production -- "
cd && cd willtheywin-fast
git branch
git status
git checkout main
git fetch
git pull

echo "building containers..."
docker-compose -f docker-compose-prod.yml up --build -d
docker ps

docker exec will_they_win_fast_api_prod bash -c "alembic upgrade head"

echo " -- Deploying willtheywin-fast production complete -- "
