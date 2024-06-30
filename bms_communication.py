import serial
import socket

def connect_to_bms(interface='serial', serial_port=None, baud_rate=None, ethernet_ip=None, ethernet_port=None):
    if interface == 'serial' and serial_port and baud_rate:
        try:
            print("Trying to connect " + serial_port + ":" + str(baud_rate))
            ser = serial.Serial(serial_port, baud_rate, timeout = 1)
            print(f"Connected to BMS over serial port: {serial_port} with baud rate: {baud_rate}")
            return ser
        except serial.SerialException as e:
            print(f"Serial connection error: {e}")
            return None
    elif interface == 'ethernet' and ethernet_ip and ethernet_port:
        try:
            print("Trying to connect " + ethernet_ip + ":" + str(ethernet_port))
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((ethernet_ip, ethernet_port))
            print(f"Connected to BMS over Ethernet: {ethernet_ip}:{ethernet_port}")
            return sock
        except socket.error as e:
            print(f"Ethernet connection error: {e}")
            return None
    else:
        print("Invalid parameters or interface selection.")
        return None

def send_data_to_bms(bms_connection, data):
    try:
        # Ensure data is in bytes format
        if isinstance(data, str):
            data = data.encode()  # Convert string to bytes if necessary

        # Check if the connection is a socket (Ethernet)
        if hasattr(bms_connection, 'send'):
            bms_connection.send(data)
        # Check if the connection is a serial connection
        elif hasattr(bms_connection, 'write'):
            bms_connection.write(data)
        else:
            raise ValueError("Unsupported connection type")

        return True

    except Exception as e:
        print(f"Error sending data to BMS: {e}")
        return False

def receive_data_from_bms(bms_connection):
    try:
        # Check if the connection is a serial connection
        if hasattr(bms_connection, 'readline'):
            received_data = bms_connection.readline().decode().strip()
        # Check if the connection is a socket (Ethernet)
        elif hasattr(bms_connection, 'recv'):
            # Assuming a buffer size of 1024 bytes for demonstration purposes
            received_data = bms_connection.recv(socket_buffer_size).decode().strip()
        else:
            raise ValueError("Unsupported connection type")

        print(f"Received data from BMS: {received_data}")
        return received_data
    except Exception as e:
        print(f"Error receiving data from BMS: {e}")
        return None

