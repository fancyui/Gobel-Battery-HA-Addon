ARG BUILD_FROM
FROM $BUILD_FROM

# Install Python3, pip3, and build dependencies
RUN apk update && apk add --no-cache python3 py3-pip build-base
RUN apk update && apk add --no-cache py3-pyserial build-base
RUN apk update && apk add --no-cache py3-paho-mqtt build-base

# Copy requirements.txt and install Python dependencies
COPY requirements.txt /tmp/
#RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Set working directory to our add-on persistent data directory
WORKDIR /data

# Copy data for add-on
COPY run.sh /
COPY bms_script.py /
RUN chmod +x /run.sh

# Set the default command
CMD [ "/run.sh" ]
