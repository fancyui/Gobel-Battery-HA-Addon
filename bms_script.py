def parse_all_pack_analog_ascii_response(response):
    """
    Parses the ASCII response string to extract pack analog data for multiple packs.

    Args:
    response (str): The ASCII response string from the BMS.

    Returns:
    list: Parsed data containing pack analog information for each pack.
    """
    packs_data = []
    
    # Split the response into fields
    fields = response.split()
    
    # Check the command and response validity
    if fields[3] != '46' or fields[4] != '00':
        raise ValueError("Invalid command or response code")
    
    # Extract the length of the data information
    length = int(fields[5], 16)
    
    # Start parsing the data information
    offset = 6  # Start after fixed header fields

    # Number of packs
    num_packs = int(fields[offset], 16)
    offset += 1

    for _ in range(num_packs):
        pack_data = {}

        # Number of cells
        num_cells = int(fields[offset], 16)
        offset += 1
        pack_data['num_cells'] = num_cells

        # Cell voltages
        cell_voltages = []
        for _ in range(num_cells):
            voltage = int(fields[offset], 16) / 1000  # Convert mV to V
            cell_voltages.append(voltage)
            offset += 1
        pack_data['cell_voltages'] = cell_voltages

        # Number of temperature sensors
        num_temps = int(fields[offset], 16)
        offset += 1
        pack_data['num_temps'] = num_temps

        # Temperatures
        temperatures = []
        for _ in range(num_temps):
            temperature = int(fields[offset], 16) / 10  # Convert tenths of degrees to degrees
            temperatures.append(temperature)
            offset += 1
        pack_data['temperatures'] = temperatures

        # Pack current
        pack_current = int(fields[offset], 16) / 100  # Convert 10mA to A
        offset += 1
        pack_data['pack_current'] = pack_current

        # Pack total voltage
        pack_total_voltage = int(fields[offset], 16) / 100  # Convert mV to V
        offset += 1
        pack_data['pack_total_voltage'] = pack_total_voltage

        # Pack remaining capacity
        pack_remain_capacity = int(fields[offset], 16) * 10  # Convert 10mAH to mAH
        offset += 1
        pack_data['pack_remain_capacity'] = pack_remain_capacity

        # Pack full capacity
        pack_full_capacity = int(fields[offset], 16) * 10  # Convert 10mAH to mAH
        offset += 1
        pack_data['pack_full_capacity'] = pack_full_capacity

        # Pack design capacity
        pack_design_capacity = int(fields[offset], 16) * 10  # Convert 10mAH to mAH
        offset += 1
        pack_data['pack_design_capacity'] = pack_design_capacity

        packs_data.append(pack_data)

    return packs_data

# Example usage with a hypothetical ASCII response string
response = "7E 32 35 30 30 34 36 30 30 46 30 37 00 02 03E8 03E8 03E8 02 1F4 1F4 07D0 07D0 07D0 03 1F4 1F4 07D0 07D0 07D0"
data = parse_all_pack_analog_ascii_response(response)
print(data)

def send_data_to_bms(command):
    """
    Generates a request to send to the BMS to get specific data based on the command parameter.

    Parameters:
    command (str): The command to send to the BMS. It can be one of the following:
                   - 'analog_data' for getting all pack analog information.
                   - 'warning_data' for getting pack warning information.
                   - 'capacity_data' for getting pack capacity information.
    
    Returns:
    bytes: The request message to be sent to the BMS.
    """
    
    SOI = '~'
    VER = '32'
    ADR = '35'
    COMMON_PART = '30 30 34 36'
    
    if command == 'analog_data':
        CID2 = '42'
    elif command == 'warning_data':
        CID2 = '44'
    elif command == 'capacity_data':
        CID2 = 'A6'
    else:
        raise ValueError("Invalid command")
    
    # Length of the INFO data in ASCII characters, set to 02H for all commands
    LENID = '02'
    
    # Command for all packs, set to FFH for getting all pack information
    COMMAND = 'FF'
    
    # Placeholder for length, checksum, and EOI to be calculated later
    LENGTH_PLACEHOLDER = '00 00'
    CHKSUM_PLACEHOLDER = '00'
    EOI = '\r'
    
    # Construct the message without length and checksum
    message_without_length_checksum = f"{SOI} {VER} {ADR} {COMMON_PART} {CID2} {LENID} {COMMAND}"
    
    # Calculate the length (excluding SOI and EOI)
    length = len(message_without_length_checksum.split())
    
    # Calculate the checksum
    checksum = 0
    for char in message_without_length_checksum.replace(" ", ""):
        checksum += ord(char)
    checksum = (0x10000 - (checksum % 0x10000)) & 0xFFFF
    
    # Format checksum in hex
    checksum_hex = f"{checksum:04X}"
    
    # Construct the final message
    message = f"{message_without_length_checksum} {LENGTH_PLACEHOLDER} {checksum_hex} {EOI}"
    
    return message.encode('ascii')

# Example usage
request_message = send_data_to_bms('analog_data')
print(request_message)

