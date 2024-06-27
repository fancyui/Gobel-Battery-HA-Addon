def parse_bms_ascii_response(response):
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
data = parse_ascii_response(response)
print(data)
