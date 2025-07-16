#!/usr/bin/with-contenv bashio
set -e

echo "Pace BMS Monitor Starting..."

python3 -u /sensor.py
