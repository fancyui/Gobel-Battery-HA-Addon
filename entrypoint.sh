#!/bin/sh

# Start your custom script
setsid /run.sh &

# Start Nginx
nginx -g "daemon off; error_log /dev/stdout debug;"