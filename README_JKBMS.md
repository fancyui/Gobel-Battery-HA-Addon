# 极空BMS RS485 Modbus协议实现

## 概述

这个项目实现了对极空BMS（JK-BMS）RS485 Modbus通信协议的支持，基于官方协议文档V1.1版本。

## 核心功能

### 1. JKBMSModbus 类

主要的通信类，提供了完整的Modbus协议实现：

```python
from jkbms_modbus import JKBMSModbus

# 创建实例
jk_bms = JKBMSModbus(debug=True)

# 读取单体电压1
command = jk_bms.build_read_cellvol1_command()
```

### 2. 核心方法

#### 指令构建
- `build_read_cellvol1_command()` - 构建读取单体电压1的指令
- `build_read_all_cell_voltages_command()` - 构建读取所有单体电压的指令
- `build_read_register_command()` - 通用寄存器读取指令构建

#### 数据解析
- `parse_register_response()` - 解析寄存器响应数据
- `get_cellvol1_voltage_mv()` - 提取单体电压1数值

#### CRC校验
- `calculate_crc16_modbus()` - 计算Modbus CRC16校验码

## 协议分析

### 寄存器地址映射

根据文档分析，极空BMS使用两个主要的寄存器区域：

1. **配置区域 (0x1000基地址)** - 设置参数
2. **数据区域 (0x1200基地址)** - 实时数据

#### 单体电压寄存器地址

基地址: 0x1200，偏移地址直接加到基地址上：

```
单体电压0: 0x1200 (基地址0x1200 + 偏移0x0000 = 0x1200)
单体电压1: 0x1202 (基地址0x1200 + 偏移0x0002 = 0x1202)  ← 目标地址
单体电压2: 0x1204 (基地址0x1200 + 偏移0x0004 = 0x1204)
...
```

### 单体电压1读取指令分析

根据文档要求构建的读取单体电压1指令：

```
指令格式: 地址码 + 功能码 + 起始地址 + 寄存器数量 + CRC校验
        01     03      12 02       00 01      [CRC]
```

**指令详解：**
- `01H` - 从机地址（可配置）
- `03H` - 功能码（读取保持寄存器）
- `12 02H` - 起始寄存器地址0x1202（高字节在前）
- `00 01H` - 读取1个寄存器（高字节在前）
- `[CRC]` - CRC16校验码（低字节在前）

## 使用示例

### 基本使用

```python
#!/usr/bin/env python3

from jkbms_modbus import JKBMSModbus

# 初始化
jk_bms = JKBMSModbus(debug=True)

# 构建读取单体电压1的指令
command = jk_bms.build_read_cellvol1_command()
print(f"指令: {command.hex().upper()}")

# 假设从串口接收到响应数据
response = receive_from_serial()  # 你的串口接收函数

# 解析电压值
voltage_mv = jk_bms.get_cellvol1_voltage_mv(response)
if voltage_mv is not None:
    print(f"单体电压1: {voltage_mv} mV ({voltage_mv/1000:.3f} V)")
```

### 读取多个单体电压

```python
# 读取前16个单体电压
command = jk_bms.build_read_all_cell_voltages_command(16)
print(f"读取16个单体电压指令: {command.hex().upper()}")
```

### 设置从机地址

```python
# 设置从机地址为5
jk_bms.set_slave_address(5)
command = jk_bms.build_read_cellvol1_command()
```

## 通信参数

根据文档规范：

- **通信接口**: UART
- **电平标准**: RS485
- **波特率**: 115200bps
- **数据位**: 8
- **停止位**: 1
- **校验位**: 无

## 测试

运行测试脚本验证功能：

```bash
python test_jkbms.py
```

测试包括：
1. 指令构建验证
2. CRC校验测试
3. 响应解析测试

## 文件结构

```
jkbms_modbus.py     # 主要的Modbus通信实现
test_jkbms.py       # 测试脚本
README_JKBMS.md     # 本说明文档
```

## 支持的数据类型

- **单体电压**: UINT16, 单位mV, 精度1mV
- **电池总电压**: UINT32, 单位mV
- **电池电流**: INT32, 单位mA
- **电池功率**: UINT32, 单位mW
- **电池温度**: INT16, 单位0.1℃
- **SOC**: UINT8, 单位%

## 错误处理

代码包含完整的错误处理：

1. **CRC校验错误** - 自动检测并报告
2. **数据长度错误** - 验证响应数据完整性
3. **功能码错误** - 确认响应匹配请求
4. **参数验证** - 检查地址范围等

## 注意事项

1. **字节序**: Modbus使用大端字节序（高字节在前）
2. **CRC校验**: 使用标准Modbus CRC16算法
3. **地址映射**: 字节偏移需要除以2转换为寄存器地址
4. **通信时序**: 需要适当的延时确保通信稳定

## 扩展功能

可以基于这个实现扩展更多功能：

- 写入配置参数
- 读取报警状态
- 控制充放电开关
- 读取温度传感器数据
- 获取电池循环次数等统计信息

## 协议版本

基于极空BMS RS485 Modbus通用协议V1.1版本实现。 