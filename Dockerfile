ARG BUILD_FROM
FROM $BUILD_FROM

# Install Python3, pip3, and build dependencies
RUN apk update && apk add --no-cache \
    python3 \
    py3-pip \
    py3-pyserial \
    py3-paho-mqtt \
    py3-requests \
    build-base

run \
    apk --no-cache add \
        nginx \
    \
    && mkdir -p /run/nginx



# RUN apk update && apk add --no-cache libyaml build-base

# Copy requirements.txt and install Python dependencies
# COPY requirements.txt /tmp/
# RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Set working directory to our add-on persistent data directory
WORKDIR /data

# Copy data for add-on
COPY run.sh /
COPY sensor.py /
COPY pacebms.py /
COPY bms_comm.py /
COPY ha_rest_api.py /
COPY ha_mqtt.py /
COPY config.yaml /
COPY dashboard_generator.py /
COPY ingress.conf /etc/nginx/http.d/

RUN chmod +x /run.sh

# Set the default command
CMD [ "/run.sh" ]

CMD [ "nginx", "-g", "daemonn off; error_log /dev/stdout debug;" ]
