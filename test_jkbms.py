#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试极空BMS Modbus指令构建
"""

from jkbms_modbus import JKBMSModbus

def test_build_cellvol1_command():
    """测试构建读取单体电压1的指令"""
    print("=== 测试极空BMS Modbus指令构建 ===")
    
    # 创建JK BMS实例
    jk_bms = JKBMSModbus(debug=True)
    
    # 构建读取单体电压1的指令
    print("\n1. 构建读取单体电压1(CellVol1)的指令:")
    command = jk_bms.build_read_cellvol1_command()
    command_hex = command.hex().upper()
    print(f"指令(HEX): {command_hex}")
    
    # 分解指令
    print("\n2. 指令分解:")
    print(f"地址码: {command[0]:02X}H")
    print(f"功能码: {command[1]:02X}H (读取寄存器)")
    print(f"起始寄存器地址: {(command[2] << 8) | command[3]:04X}H")
    print(f"寄存器数量: {(command[4] << 8) | command[5]:04X}H")
    print(f"CRC校验: {command[6]:02X}{command[7]:02X}H")
    
    # 验证应该的结果
    print(f"\n3. 期望结果分析:")
    print(f"- 从机地址: 01H")
    print(f"- 功能码: 03H (读取寄存器)")
    print(f"- 寄存器地址: 1202H (单体电压1，偏移0x0002)")
    print(f"- 读取数量: 0001H (1个寄存器)")
    
    return command

def test_build_all_cell_voltages():
    """测试构建读取所有单体电压的指令"""
    print("\n=== 测试读取所有单体电压 ===")
    
    jk_bms = JKBMSModbus(debug=True)
    
    # 构建读取16个单体电压的指令
    command = jk_bms.build_read_all_cell_voltages_command(16)
    command_hex = command.hex().upper()
    print(f"读取16个单体电压指令(HEX): {command_hex}")
    
    return command

def test_parse_response():
    """测试解析响应数据"""
    print("\n=== 测试响应解析 ===")
    
    jk_bms = JKBMSModbus(debug=True)
    
    # 模拟一个单体电压1的响应 (3.3V = 3300mV)
    # 响应格式: 地址码 + 功能码 + 字节数 + 数据 + CRC
    mock_response = bytes([
        0x01,           # 地址码
        0x03,           # 功能码
        0x02,           # 字节数 (1个UINT16 = 2字节)
        0x0C, 0xE4,     # 3300 (0x0CE4) = 3.3V
        0x00, 0x00      # CRC (这里用0占位，实际需要计算)
    ])
    
    # 重新计算正确的CRC
    data_without_crc = mock_response[:-2]
    calculated_crc = jk_bms.calculate_crc16_modbus(data_without_crc)
    mock_response = data_without_crc + bytes([(calculated_crc & 0xFF), (calculated_crc >> 8)])
    
    print(f"模拟响应数据: {mock_response.hex().upper()}")
    
    # 解析响应
    voltage = jk_bms.get_cellvol1_voltage_mv(mock_response)
    print(f"解析得到的单体电压1: {voltage} mV")
    
    return voltage

if __name__ == "__main__":
    # 运行测试
    cmd1 = test_build_cellvol1_command()
    cmd2 = test_build_all_cell_voltages()
    voltage = test_parse_response()
    
    print(f"\n=== 总结 ===")
    print(f"单体电压1读取指令: {cmd1.hex().upper()}")
    print(f"16个单体电压读取指令: {cmd2.hex().upper()}")
    print(f"模拟解析电压值: {voltage} mV") 