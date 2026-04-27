#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JK BMS RS485 Frame Diagnostic Tool
===================================
Connects to JK BMS via RS485-to-WiFi, sends query commands,
and analyzes the 55AA data frames to verify parser offsets.

Usage:
  python diagnose_jkbms.py --ip <BMS_IP> --port <BMS_PORT>
  python diagnose_jkbms.py --ip 192.168.1.100 --port 1234

If no arguments given, will prompt for connection details.
"""

import sys
import os
import argparse
import logging

# Add project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bms_comm import BMSCommunication
from jkbms_rs485 import JKBMS485


def create_bms_comm(ip, port):
    """Create BMS communication instance over ethernet."""
    bms_comm = BMSCommunication(
        interface='ethernet',
        ethernet_ip=ip,
        ethernet_port=port,
        buffer_size=4096,
        debug=True
    )
    return bms_comm


def analyze_dynamic_frame(jkbms):
    """Query dynamic data and show frame analysis."""
    print("\n" + "=" * 70)
    print("QUERYING DYNAMIC DATA (register 0x1620)")
    print("=" * 70)

    command = jkbms.build_write_command(jkbms.REG_DYNAMIC)
    print(f"Command: {command.hex().upper()}")

    raw = jkbms.send_and_receive(command)
    if not raw:
        print("ERROR: No response received!")
        return None

    print(f"Raw response: {len(raw)} bytes")
    print(f"Raw hex: {raw.hex().upper()}")

    # Find and extract 55AA frame
    idx = raw.find(b'\x55\xAA')
    if idx < 0:
        print("ERROR: No 55AA frame found in response!")
        return None

    frame = raw[idx:]
    print(f"55AA frame at offset {idx}, {len(frame)} bytes")

    # Print full hex with offset markers
    print("\n--- RAW 55AA FRAME (hex) ---")
    for row in range(0, len(frame), 16):
        row_data = frame[row:row + 16]
        hex_part = ' '.join(f'{b:02X}' for b in row_data)
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in row_data)
        print(f"  {row:04X}: {hex_part:<48s} |{ascii_part}|")

    # Run the frame analysis
    print("\n--- FRAME FIELD ANALYSIS ---")
    jkbms.dump_frame_analysis(frame)

    # Parse and show result
    result = jkbms.parse_jkbms_55aa_frame(frame)
    print("\n--- PARSED VALUES ---")
    if not result:
        print("  (empty - no fields parsed)")
    else:
        for k in sorted(result.keys()):
            v = result[k]
            if k == 'cell_voltages':
                print(f"  {k} (mV): {v}")
                if v:
                    print(f"    → total: {sum(v)/1000:.3f}V, avg: {sum(v)/len(v)/1000:.3f}V")
            elif k == 'device_name':
                print(f"  {k}: {repr(v)}")
            elif isinstance(v, list):
                print(f"  {k}: {[round(x, 1) if isinstance(x, float) else x for x in v]}")
            elif isinstance(v, float):
                print(f"  {k}: {v:.3f}")
            else:
                print(f"  {k}: {v}")

    return result


def analyze_static_frame(jkbms):
    """Query static data and show frame analysis."""
    print("\n" + "=" * 70)
    print("QUERYING STATIC DATA (register 0x161C)")
    print("=" * 70)

    command = jkbms.build_write_command(jkbms.REG_STATIC)
    print(f"Command: {command.hex().upper()}")

    raw = jkbms.send_and_receive(command)
    if not raw:
        print("No response for static data")
        return

    print(f"Raw response: {len(raw)} bytes")
    print(f"Raw hex: {raw.hex().upper()}")

    idx = raw.find(b'\x55\xAA')
    if idx < 0:
        print("No 55AA frame in static response")
        return

    frame = raw[idx:]
    print(f"55AA frame at offset {idx}, {len(frame)} bytes")

    result = jkbms.parse_jkbms_static_frame(frame)
    print("\n--- STATIC DATA ---")
    for k, v in result.items():
        print(f"  {k}: {v}")


def analyze_alarm_frame(jkbms):
    """Query alarm data."""
    print("\n" + "=" * 70)
    print("QUERYING ALARM DATA (register 0x12A0, FC 0x03)")
    print("=" * 70)

    command = jkbms.build_read_command(jkbms.REG_ALARM, 2)
    print(f"Command: {command.hex().upper()}")

    raw = jkbms.send_and_receive(command)
    if not raw:
        print("No response for alarm data")
        return

    print(f"Raw response: {len(raw)} bytes")
    print(f"Raw hex: {raw.hex().upper()}")

    result = jkbms.parse_alarm_response(raw)
    if result:
        print(f"\n  Raw alarm value: 0x{result['raw_value']:08X}")
        print(f"  Has alarms: {result['has_alarms']}")
        print(f"  Active alarms: {result['active_count']}")
        if result['has_alarms']:
            for desc, active in result['alarms'].items():
                if active:
                    print(f"    ⚠ {desc}")
    else:
        print("  Failed to parse alarm response")


def main():
    parser = argparse.ArgumentParser(description='JK BMS Frame Diagnostic Tool')
    parser.add_argument('--ip', help='BMS IP address')
    parser.add_argument('--port', type=int, help='BMS TCP port')
    args = parser.parse_args()

    ip = args.ip or input("BMS IP address: ").strip()
    port = args.port or int(input("BMS TCP port: ").strip())

    # Turn off logging noise from libraries
    logging.basicConfig(level=logging.WARNING)

    # Connect
    print(f"\nConnecting to JK BMS at {ip}:{port}...")
    bms_comm = create_bms_comm(ip, port)
    conn = bms_comm.connect()
    if not conn:
        print("FAILED to connect!")
        sys.exit(1)

    print("Connected!")

    # Create JKBMS485 instance with debug on
    jkbms = JKBMS485(bms_comm, None, 'jkbms', 10, debug=True, if_random=False)

    try:
        # Analyze dynamic frame (main data)
        dyn_result = analyze_dynamic_frame(jkbms)

        if dyn_result:
            # Show what looks correct vs needs calibration
            cells = dyn_result.get('cell_voltages', [])
            soc = dyn_result.get('soc')
            voltage = dyn_result.get('voltage_v')
            current = dyn_result.get('current_a')

            print("\n" + "=" * 70)
            print("FIELD VERIFICATION CHECKLIST")
            print("=" * 70)
            print(f"  ✅ Cell voltages: {len(cells)} cells (confirmed)")
            print(f"  ✅ SOC: {soc}% (confirmed)")
            print(f"  ✅ Total voltage: {voltage:.2f}V (confirmed)")
            print(f"  ⚠ Current: {current}A (UNCONFIRMED - check against app!)")
            for temp_key in ['temp_mos', 'temp_bat1', 'temp_bat2', 'temp_bat3', 'temp_bat4']:
                if temp_key in dyn_result:
                    print(f"  ⚠ {temp_key}: {dyn_result[temp_key]}°C (UNCONFIRMED)")
            for cap_key in ['remain_capacity_ah', 'full_capacity_ah']:
                if cap_key in dyn_result:
                    print(f"  ⚠ {cap_key}: {dyn_result[cap_key]}Ah (UNCONFIRMED)")

        # Analyze static frame
        analyze_static_frame(jkbms)

        # Analyze alarm frame
        analyze_alarm_frame(jkbms)

    finally:
        bms_comm.disconnect()
        print("\nDisconnected.")


if __name__ == '__main__':
    main()
