import serial
import time
import os
import binascii
import paho.mqtt.client as mqtt

# Load configuration from environment variables
# serial_port = os.getenv('SERIAL_PORT', '/dev/ttyUSB0')
# baud_rate = int(os.getenv('BAUD_RATE', 9600))

serial_port = '/dev/ttyUSB0'
baud_rate = 9600

# MQTT settings
broker = "homeassistant.local"  # Change to your MQTT broker address
port = 1883
topic = "homeassistant/sensor/bms_raw"
client_id = "bms_client"

# Initialize MQTT client
client = mqtt.Client(client_id)
client.connect(broker, port)

def read_from_bms(ser):
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').rstrip()
        print(f"Received: {line}")

        # Publish the raw data to the MQTT broker
        client.publish(topic, line)
        print(f"Published: {line}")

def send_to_bms(ser, data):
    ser.write(data)
    ser.flush()
    print(f"Sent: {binascii.hexlify(data).decode('utf-8')}")

def main():
    ser = serial.Serial(serial_port, baud_rate, timeout=1)
    time.sleep(2)  # Wait for the serial connection to initialize

    # The data to send to the BMS
    data_to_send = '7E 32 35 30 30 34 36 34 32 45 30 30 32 46 46 46 44 30 36 0D'
    # Convert the hex string to bytes
    data_bytes = binascii.unhexlify(data_to_send.replace(' ', ''))

    try:
        while True:
            # Send data to the BMS every 5 seconds
            send_to_bms(ser, data_bytes)
            
            # Read data from the BMS
            read_from_bms(ser)
            
            time.sleep(5)
    except KeyboardInterrupt:
        ser.close()

if __name__ == "__main__":
    main()
