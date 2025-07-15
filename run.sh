#!/usr/bin/with-contenv bashio
set -e

echo "Gobel Power BMS Monitor Starting..."

python3 -u /sensor.py
