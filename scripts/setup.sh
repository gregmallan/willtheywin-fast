#!/usr/bin/env bash
set -e

cd ..
alembic upgrade head
python seedall.py
