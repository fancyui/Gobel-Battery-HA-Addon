#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
极空BMS RS485 Modbus通信协议实现
支持读取单体电压等各种参数
"""

import struct
import logging

class JKBMSModbus:
    
    def __init__(self, debug=False):
        """
        初始化极空BMS Modbus通信类
        
        Args:
            debug (bool): 是否启用调试模式
        """
        # 配置日志
        logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # 默认从机地址
        self.default_slave_address = 0x01
        
        # 功能码定义
        self.FUNCTION_CODE_READ_HOLDING_REGISTERS = 0x03
        self.FUNCTION_CODE_WRITE_MULTIPLE_REGISTERS = 0x10
        
        # 寄存器地址定义 (基于文档中的寄存器映射表)
        # 注意：基地址0x1200，偏移地址直接加到基地址上
        # 单体电压1偏移: 0x0002 = 寄存器地址 0x1200 + 0x0002 = 0x1202
        self.REGISTER_ADDRESSES = {
            'CellVol0': 0x1200,      # 单体电压0 (基地址0x1200 + 偏移0x0000 = 0x1200)
            'CellVol1': 0x1202,      # 单体电压1 (基地址0x1200 + 偏移0x0002 = 0x1202)
            'CellVol2': 0x1204,      # 单体电压2 (基地址0x1200 + 偏移0x0004 = 0x1204)
            'CellVol3': 0x1206,      # 单体电压3 (基地址0x1200 + 偏移0x0006 = 0x1206)
            'CellVol4': 0x1208,      # 单体电压4 (基地址0x1200 + 偏移0x0008 = 0x1208)
            'CellVol5': 0x120A,      # 单体电压5 (基地址0x1200 + 偏移0x000A = 0x120A)
            'CellVol6': 0x120C,      # 单体电压6 (基地址0x1200 + 偏移0x000C = 0x120C)
            'CellVol7': 0x120E,      # 单体电压7 (基地址0x1200 + 偏移0x000E = 0x120E)
            'CellVol8': 0x1210,      # 单体电压8 (基地址0x1200 + 偏移0x0010 = 0x1210)
            'CellVol9': 0x1212,      # 单体电压9 (基地址0x1200 + 偏移0x0012 = 0x1212)
            'CellVol10': 0x1214,     # 单体电压10 (基地址0x1200 + 偏移0x0014 = 0x1214)
            'CellVol11': 0x1216,     # 单体电压11 (基地址0x1200 + 偏移0x0016 = 0x1216)
            'CellVol12': 0x1218,     # 单体电压12 (基地址0x1200 + 偏移0x0018 = 0x1218)
            'CellVol13': 0x121A,     # 单体电压13 (基地址0x1200 + 偏移0x001A = 0x121A)
            'CellVol14': 0x121C,     # 单体电压14 (基地址0x1200 + 偏移0x001C = 0x121C)
            'CellVol15': 0x121E,     # 单体电压15 (基地址0x1200 + 偏移0x001E = 0x121E)
            'BatVol': 0x1290,        # 电池总电压 (基地址0x1200 + 偏移0x0090 = 0x1290)
            'BatCurrent': 0x1298,    # 电池电流 (基地址0x1200 + 偏移0x0098 = 0x1298)
            'BatWatt': 0x1294,       # 电池功率 (基地址0x1200 + 偏移0x0094 = 0x1294)
            'SOC': 0x12A6,           # 剩余电量SOC (基地址0x1200 + 偏移0x00A6 = 0x12A6)
            'TempBat1': 0x129C,      # 电池温度1 (基地址0x1200 + 偏移0x009C = 0x129C)
            'TempBat2': 0x129E,      # 电池温度2 (基地址0x1200 + 偏移0x009E = 0x129E)
        }

    def calculate_crc16_modbus(self, data):
        """
        计算Modbus CRC16校验码
        
        Args:
            data (bytes): 需要计算CRC的数据
            
        Returns:
            int: CRC16校验码
        """
        crc = 0xFFFF
        
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
                    
        return crc

    def build_read_register_command(self, register_address, register_count=1, slave_address=None):
        """
        构建读取寄存器的Modbus指令
        
        Args:
            register_address (int): 寄存器起始地址
            register_count (int): 要读取的寄存器数量，默认为1
            slave_address (int): 从机地址，默认使用类初始化时的地址
            
        Returns:
            bytes: 构建的Modbus指令
        """
        if slave_address is None:
            slave_address = self.default_slave_address
            
        # 构建指令帧 (不包含CRC)
        command_frame = struct.pack('>BBHH', 
                                  slave_address,                              # 地址码 (1字节)
                                  self.FUNCTION_CODE_READ_HOLDING_REGISTERS,  # 功能码 (1字节) 
                                  register_address,                           # 起始寄存器地址 (2字节，高字节在前)
                                  register_count)                             # 寄存器数量 (2字节，高字节在前)
        
        # 计算CRC校验
        crc = self.calculate_crc16_modbus(command_frame)
        
        # 添加CRC校验 (低字节在前，高字节在后)
        command_with_crc = command_frame + struct.pack('<H', crc)
        
        self.logger.debug(f"新构建的指令: {command_with_crc.hex().upper()}")
        
        return command_with_crc

    def build_read_cellvol1_command(self, slave_address=None):
        """
        构建读取单体电压1(CellVol1)的指令
        
        根据文档：
        - 寄存器地址: 0x1002 (对应0x0002偏移)
        - 数据类型: UINT16
        - 长度: 2字节
        - 单位: mV
        
        Args:
            slave_address (int): 从机地址，默认为0x01
            
        Returns:
            bytes: 读取单体电压1的Modbus指令
        """
        register_address = self.REGISTER_ADDRESSES['CellVol1']
        
        self.logger.info(f"新构建读取单体电压1(CellVol1)指令，寄存器地址: 0x{register_address:04X}")
        
        return self.build_read_register_command(register_address, 1, slave_address)

    def build_read_all_cell_voltages_command(self, cell_count=16, slave_address=None):
        """
        构建读取所有单体电压的指令
        
        Args:
            cell_count (int): 单体数量，默认16个
            slave_address (int): 从机地址，默认为0x01
            
        Returns:
            bytes: 读取所有单体电压的Modbus指令
        """
        register_address = self.REGISTER_ADDRESSES['CellVol0']  # 从第一个单体电压开始
        
        self.logger.info(f"构建读取{cell_count}个单体电压指令，起始地址: 0x{register_address:04X}")
        
        return self.build_read_register_command(register_address, cell_count, slave_address)

    def parse_register_response(self, response):
        """
        解析寄存器读取响应
        
        Args:
            response (bytes): BMS返回的响应数据
            
        Returns:
            list: 解析后的寄存器值列表
        """
        if len(response) < 5:
            self.logger.error("响应数据长度不足")
            return None
            
        # 验证CRC校验
        data_without_crc = response[:-2]
        received_crc = struct.unpack('<H', response[-2:])[0]
        calculated_crc = self.calculate_crc16_modbus(data_without_crc)
        
        if received_crc != calculated_crc:
            self.logger.error(f"CRC校验失败: 接收到={received_crc:04X}, 计算得出={calculated_crc:04X}")
            return None
            
        # 解析响应数据
        slave_address = response[0]
        function_code = response[1]
        byte_count = response[2]
        
        if function_code != self.FUNCTION_CODE_READ_HOLDING_REGISTERS:
            self.logger.error(f"功能码不匹配: {function_code:02X}")
            return None
            
        # 提取寄存器数据
        register_data = response[3:3+byte_count]
        register_values = []
        
        # 每个寄存器2字节，高字节在前
        for i in range(0, len(register_data), 2):
            if i+1 < len(register_data):
                value = struct.unpack('>H', register_data[i:i+2])[0]
                register_values.append(value)
                
        return register_values

    def get_cellvol1_voltage_mv(self, response):
        """
        从响应中提取单体电压1的值
        
        Args:
            response (bytes): BMS返回的响应数据
            
        Returns:
            int: 单体电压1的值，单位mV；失败返回None
        """
        register_values = self.parse_register_response(response)
        
        if register_values and len(register_values) > 0:
            voltage_mv = register_values[0]
            self.logger.info(f"单体电压1: {voltage_mv} mV ({voltage_mv/1000:.3f} V)")
            return voltage_mv
            
        return None

    def set_slave_address(self, address):
        """
        设置从机地址
        
        Args:
            address (int): 从机地址 (1-247)
        """
        if 1 <= address <= 247:
            self.default_slave_address = address
            self.logger.info(f"从机地址设置为: {address}")
        else:
            raise ValueError("从机地址必须在1-247范围内")

# 示例使用
if __name__ == "__main__":
    # 创建JK BMS实例
    jk_bms = JKBMSModbus(debug=True)
    
    # 构建读取单体电压1的指令
    command = jk_bms.build_read_cellvol1_command()
    print(f"读取单体电压1指令: {command.hex().upper()}")
    
    # 构建读取所有16个单体电压的指令
    command_all = jk_bms.build_read_all_cell_voltages_command(16)
    print(f"读取所有单体电压指令: {command_all.hex().upper()}") 