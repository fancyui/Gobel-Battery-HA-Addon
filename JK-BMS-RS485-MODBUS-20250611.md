[Part 1 OCR failed: OCR处理失败 (openrouter): socket hang up]

## 版本记录

<table>
  <tr>
    <th colspan="4">版本记录</th>
  </tr>
  <tr>
    <th>日期</th>
    <th>版本号</th>
    <th>描述</th>
    <th>作者</th>
  </tr>
  <tr>
    <td>2023.02</td>
    <td>V1.0</td>
    <td>1.编写通信协议;</td>
    <td>张 鹏</td>
  </tr>
  <tr>
    <td>2024.01</td>
    <td>V1.1</td>
    <td>1.修订部分错误,新增一些寄存器支持</td>
    <td>张 鹏</td>
  </tr>
</table>

## 极空BMS RS485 Modbus通用协议(V1.1)

极空BMS RS485 Modbus通用协议在数据通讯上采用主从应答的方式进行。只能由主机通过唯一从机地址发起请求，BMS(从机)根据主机请求进行响应，即半双工通讯。该协议只允许主机发起请求，从机进行被动响应，因此从机不会主动占用通讯线路造成数据冲突。

## 一、物理接口

通信物理接口的电气特性如下：

<table>
  <tr>
    <td>通信接口</td>
    <td>UART</td>
  </tr>
  <tr>
    <td>电平标准</td>
    <td>RS485</td>
  </tr>
  <tr>
    <td>波特率</td>
    <td>115200bps</td>
  </tr>
  <tr>
    <td>数据位</td>
    <td>8</td>
  </tr>
  <tr>
    <td>停止位</td>
    <td>1</td>
  </tr>
  <tr>
    <td>校验位</td>
    <td>无</td>
  </tr>
</table>

## 二、协议格式

信息传输为异步方式，使用16进制进行通讯，信息帧格式：

<table>
  <tr>
    <td>地址码</td>
    <td>功能码</td>
    <td>数据区</td>
    <td>CRC校验</td>
  </tr>
  <tr>
    <td>1字节</td>
    <td>1字节</td>
    <td>1字节</td>
    <td>2字节</td>
  </tr>
</table>

**1)地址码**

地址码是每个通讯信息帧的第一个字节，支持1到247，每个从机在总线上地址必须唯一，只有与主机发送的地址码相符的从机才能响应返回数据。

**2)功能码**

功能码是每个通讯信息帧的第二个字节。主机发送，通过功能码告知从机设备应当执行何种操作。功能码的定义如下：

<table>
  <tr>
    <td>功能</td>
    <td>定义</td>
    <td>操作</td>
  </tr>
  <tr>
    <td>03H</td>
    <td>读寄存器</td>
    <td>读取一个或者多个寄存器的数据</td>
  </tr>
  <tr>
    <td>10H</td>
    <td>写寄存器</td>
    <td>向一个或者多个寄存器写入的数据</td>
  </tr>
</table>

**3)数据区**

数据区随功能码以及数据方向的不同而不同，这些数据可以是“寄存器首地址+读取寄存器数量”、“寄存器首地址+操作数据”、“寄存器首地址+操作寄存器数量+数据长度+数据”等不同的组合，在“功能码分析”详解不同功能码的数据区。

**3)CRC校验**

CRC校验用来保证数据传输的正确性和完整性。

## 三、错误反馈

地址与CRC校验错误并不会收到从机的数据反馈，其他错误将向主机返回错误码。数据帧的第二位加上0x80表示请求发生错误（非法功能码、非法数据值等），错误帧如下：

<table>
  <tr>
    <td>地址码</td>
    <td>功能码</td>
    <td>错误码区</td>
    <td>CRC校验</td>
  </tr>
  <tr>
    <td>1字节</td>
    <td>1字节</td>
    <td>1字节</td>
    <td>2字节</td>
  </tr>
</table>

错误码定义如下：

<table>
  <tr>
    <td>值</td>
    <td>名称</td>
    <td>说明</td>
  </tr>
  <tr>
    <td>01H</td>
    <td>非法的功能码</td>
    <td>不支持该功能码操作寄存器</td>
  </tr>
  <tr>
    <td>02H</td>
    <td>寄存器地址错误</td>
    <td>访问了从机禁止访问的寄存器</td>
  </tr>
  <tr>
    <td>03H</td>
    <td>数据非法</td>
    <td>数据逻辑不合法或超出限制</td>
  </tr>
  <tr>
    <td>04H</td>
    <td>CRC校验错误</td>
    <td>CRC校验错误</td>
  </tr>
</table>

## 四、信息传输过程

通讯命令由主机发送从机时，与主机发送的地址码相符的从机接收通讯命令，如果CRC校验无误，则执行相应的操作，然后把执行结果（数据）返回给主机。返回信息中包含地址码、功能码、执行后的数据以及CRC校验码。如果地址不匹配或者CRC校验出错就不返回任何信息。

## 五、功能码分析

**1)功能码03H：读取寄存器**

例如：主机要读取从机地址为01H，起始寄存器地址为05H的2个保持寄存器数据，主机发送：

<table>
  <tr>
    <td colspan="2">主机发送</td>
    <td>数据(HEX)</td>
  </tr>
  <tr>
    <td colspan="2">地址码</td>
    <td>01H</td>
  </tr>
  <tr>
    <td colspan="2">功能码</td>
    <td>03H</td>
  </tr>
  <tr>
    <td rowspan="2">起始寄存器地址</td>
    <td>高字节</td>
    <td>00H</td>
  </tr>
  <tr>
    <td>低字节</td>
    <td>05H</td>
  </tr>
  <tr>
    <td rowspan="2">寄存器数量</td>
    <td>高字节</td>
    <td>00H</td>
  </tr>
  <tr>
    <td>低字节</td>
    <td>02H</td>
  </tr>
  <tr>
    <td rowspan="2">CRC校验</td>
    <td>低字节</td>
    <td>D4H</td>
  </tr>
  <tr>
    <td>高字节</td>
    <td>0AH</td>
  </tr>
</table>

如果从机保持寄存器05H、06H的数据为1122H、3344H，从机返回：

<table>
  <tr>
    <td colspan="2">从机返回</td>
    <td>数据(HEX)</td>
  </tr>
  <tr>
    <td colspan="2">地址码</td>
    <td>01H</td>
  </tr>
  <tr>
    <td colspan="2">功能码</td>
    <td>03H</td>
  </tr>
  <tr>
    <td colspan="2">字节数</td>
    <td>04H</td>
  </tr>
  <tr>
    <td rowspan="2">寄存器05数据</td>
    <td>高字节</td>
    <td>11H</td>
  </tr>
  <tr>
    <td>低字节</td>
    <td>22H</td>
  </tr>
  <tr>
    <td rowspan="2">寄存器06数据</td>
    <td>高字节</td>
    <td>33H</td>
  </tr>
  <tr>
    <td>低字节</td>
    <td>44H</td>
  </tr>
  <tr>
    <td rowspan="2">CRC校验</td>
    <td>低字节</td>
    <td>4BH</td>
  </tr>
  <tr>
    <td>高字节</td>
    <td>C6H</td>
  </tr>
</table>

**2)功能码10H：写入寄存器**

例如：主机要把数据0005H、2233H保存到从机地址为01H，起始寄存器地址为0020H的2个寄存器中，主机发送：

<table>
  <tr>
    <td colspan="2">主机发送</td>
    <td>数据(HEX)</td>
  </tr>
  <tr>
    <td colspan="2">地址码</td>
    <td>01H</td>
  </tr>
  <tr>
    <td colspan="2">功能码</td>
    <td>10H</td>
  </tr>
  <tr>
    <td rowspan="2">起始寄存器地址</td>
    <td>高字节</td>
    <td>00H</td>
  </tr>
  <tr>
    <td>低字节</td>
    <td>20H</td>
  </tr>
  <tr>
    <td rowspan="2">寄存器数量</td>
    <td>高字节</td>
    <td>00H</td>
  </tr>
  <tr>
    <td>低字节</td>
    <td>02H</td>
  </tr>
  <tr>
    <td colspan="2">写入字节数</td>
    <td>04H</td>
  </tr>
  <tr>
    <td rowspan="2">0000H 寄存器待写入</td>
    <td>高字节</td>
    <td>00H</td>
  </tr>
  <tr>
    <td>低字节</td>
    <td>05H</td>
  </tr>
  <tr>
    <td rowspan="2">0001H 寄存器待写入</td>
    <td>高字节</td>
    <td>22H</td>
  </tr>
  <tr>
    <td>低字节</td>
    <td>33H</td>
  </tr>
  <tr>
    <td rowspan="2">CRC校验</td>
    <td>低字节</td>
    <td>B9H</td>
  </tr>
  <tr>
    <td>高字节</td>
    <td>03H</td>
  </tr>
</table>

功能码10H操作，从机返回：

<table>
  <tr>
    <td colspan="2">从机返回</td>
    <td>数据(HEX)</td>
  </tr>
  <tr>
    <td colspan="2">地址码</td>
    <td>01H</td>
  </tr>
  <tr>
    <td colspan="2">功能码</td>
    <td>10H</td>
  </tr>
  <tr>
    <td rowspan="2">起始寄存器地址</td>
    <td>高字节</td>
    <td>00H</td>
  </tr>
  <tr>
    <td>低字节</td>
    <td>20H</td>
  </tr>
  <tr>
    <td rowspan="2">寄存器数量</td>
    <td>高字节</td>
    <td>00H</td>
  </tr>
  <tr>
    <td>低字节</td>
    <td>02H</td>
  </tr>
  <tr>
    <td rowspan="2">CRC校验</td>
    <td>低字节</td>
    <td>40H</td>
  </tr>
  <tr>
    <td>高字节</td>
    <td>02H</td>
  </tr>
</table>

## 寄存器映射表 Register Map

<table>
  <tr>
    <th>起始地址位 Address Field</th>
    <th>寄存器 Index</th>
    <th>数据类型 Type</th>
    <th>长度 Len</th>
    <th>读写 R/W</th>
    <th>寄存器内容 Content</th>
    <th>单位 Unit</th>
    <th>备注 Note</th>
  </tr>
  <tr>
    <td rowspan="32">0x1000</td>
    <td>0x0000</td>
    <td>0</td>
    <td>UINT32</td>
    <td>4</td>
    <td>RW</td>
    <td>进入休眠时间 VolSmartSleep</td>
    <td>s</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0004</td>
    <td>4</td>
    <td>UINT32</td>
    <td>4</td>
    <td>RW</td>
    <td>单体欠压保护 VolCellUVP</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0008</td>
    <td>8</td>
    <td>UINT32</td>
    <td>4</td>
    <td>RW</td>
    <td>单体欠压恢复电压 VolCellUVPR</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x000C</td>
    <td>12</td>
    <td>UINT32</td>
    <td>4</td>
    <td>RW</td>
    <td>单体过压保护 VolCellOVP</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0010</td>
    <td>16</td>
    <td>UINT32</td>
    <td>4</td>
    <td>RW</td>
    <td>单体过压保护恢复电压 VolCellOVPR</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0014</td>
    <td>20</td>
    <td>UINT32</td>
    <td>4</td>
    <td>RW</td>
    <td>均衡开启压差 VolBalauTrig</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0018</td>
    <td>24</td>
    <td>UINT32</td>
    <td>4</td>
    <td>RW</td>
    <td>SOC=100%时的电压 VolSOC100%</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x001C</td>
    <td>28</td>
    <td>UINT32</td>
    <td>4</td>
    <td>RW</td>
    <td>SOC=0%时的电压 VolSOC0%</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0020</td>
    <td>32</td>
    <td>UINT32</td>
    <td>4</td>
    <td>RW</td>
    <td>整组欠压保护 VolCellUVP</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0024</td>
    <td>36</td>
    <td>UINT32</td>
    <td>4</td>
    <td>RW</td>
    <td>整组过压保护 VolCellOVP</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0028</td>
    <td>40</td>
    <td>UINT32</td>
    <td>4</td>
    <td>RW</td>
    <td>自动关机电压 VolSysPwrOff</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x002C</td>
    <td>44</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>放电过流保护 CurBatDCP</td>
    <td>mA</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0030</td>
    <td>48</td>
    <td>UINT32</td>
    <td>4</td>
    <td>RW</td>
    <td>放电过流保护延时 TIMBatCOCPDly</td>
    <td>S</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0034</td>
    <td>52</td>
    <td>UINT32</td>
    <td>4</td>
    <td>RW</td>
    <td>在放电过流释放延时 TIMBatCOCPR Dly</td>
    <td>S</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0038</td>
    <td>56</td>
    <td>UINT32</td>
    <td>4</td>
    <td>RW</td>
    <td>充电过流保护 CurBatOCC</td>
    <td>mA</td>
    <td></td>
  </tr>
  <tr>
    <td>0x003C</td>
    <td>60</td>
    <td>UINT32</td>
    <td>4</td>
    <td>RW</td>
    <td>充电过流保护延时 TIMBatOCCPDly</td>
    <td>S</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0040</td>
    <td>64</td>
    <td>UINT32</td>
    <td>4</td>
    <td>RW</td>
    <td>充电过流释放延时 TIMBatOCCPRDly</td>
    <td>S</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0044</td>
    <td>68</td>
    <td>UINT32</td>
    <td>4</td>
    <td>RW</td>
    <td>短路保护释放 TIMBatSCPRDly</td>
    <td>S</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0048</td>
    <td>72</td>
    <td>UINT32</td>
    <td>4</td>
    <td>RW</td>
    <td>电池短路保护 CurBatSCP</td>
    <td>mA</td>
    <td></td>
  </tr>
  <tr>
    <td>0x004C</td>
    <td>76</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>充电过温保护 TMPBatCOT</td>
    <td>0.1&deg;C</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0050</td>
    <td>80</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>充电过温恢复 TMPBatCOTPR</td>
    <td>0.1&deg;C</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0054</td>
    <td>84</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>放电过温保护 TMPBatDOT</td>
    <td>0.1&deg;C</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0058</td>
    <td>88</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>放电过温恢复 TMPBatDOTPR</td>
    <td>0.1&deg;C</td>
    <td></td>
  </tr>
  <tr>
    <td>0x005C</td>
    <td>92</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>充电低温保护 TMPBatCUT</td>
    <td>0.1&deg;C</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0060</td>
    <td>96</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>充电低温恢复 TMPBatCUTPR</td>
    <td>0.1&deg;C</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0064</td>
    <td>100</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>MOS过温保护 TMPMosOTP</td>
    <td>0.1&deg;C</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0068</td>
    <td>104</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>MOS过温保护恢复 TMPMosOTPR</td>
    <td>0.1&deg;C</td>
    <td></td>
  </tr>
  <tr>
    <td>0x006C</td>
    <td>108</td>
    <td>UINT32</td>
    <td>4</td>
    <td>RW</td>
    <td>电池容量 CapBatMax</td>
    <td>mAH</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0070</td>
    <td>112</td>
    <td>UINT32</td>
    <td>4</td>
    <td>RW</td>
    <td>充电开关 BatChargeEN</td>
    <td></td>
    <td>1: 打开; 0: 关闭</td>
  </tr>
  <tr>
    <td>0x0074</td>
    <td>116</td>
    <td>UINT32</td>
    <td>4</td>
    <td>RW</td>
    <td>放电开关 BatDisChargeEN</td>
    <td></td>
    <td>1: 打开; 0: 关闭</td>
  </tr>
  <tr>
    <td>0x0078</td>
    <td>120</td>
    <td>UINT32</td>
    <td>4</td>
    <td>RW</td>
    <td>均衡开关 BalanEN</td>
    <td></td>
    <td>1: 打开; 0: 关闭</td>
  </tr>
  <tr>
    <td>0x007C</td>
    <td>124</td>
    <td>UINT32</td>
    <td>4</td>
    <td>RW</td>
    <td>电池设计容量 CapBatCell</td>
    <td>mAH</td>
    <td></td>
  </tr>
  <tr>
    <td rowspan="22">0x1000</td>
    <td>0x0080</td>
    <td>128</td>
    <td>UINT32</td>
    <td>4</td>
    <td>RW</td>
    <td>短路保护延时 SCPDelay</td>
    <td>us</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0084</td>
    <td>132</td>
    <td>UINT32</td>
    <td>4</td>
    <td>RW</td>
    <td>均衡开启电压 VolBalanStart</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0088</td>
    <td>136</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>内阻校准电阻 0CellConWireRes0</td>
    <td>u&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x008C</td>
    <td>140</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>连接线内阻 1CellConWireRes1</td>
    <td>u&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0090</td>
    <td>144</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>连接线内阻 2CellConWireRes2</td>
    <td>u&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0094</td>
    <td>148</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>连接线内阻 3CellConWireRes3</td>
    <td>u&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0098</td>
    <td>152</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>连接线内阻 4CellConWireRes4</td>
    <td>u&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x009C</td>
    <td>156</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>连接线内阻 5CellConWireRes5</td>
    <td>u&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00A0</td>
    <td>160</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>连接线内阻 6CellConWireRes6</td>
    <td>u&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00A4</td>
    <td>164</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>连接线内阻 7CellConWireRes7</td>
    <td>u&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00A8</td>
    <td>168</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>连接线内阻 8CellConWireRes8</td>
    <td>u&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00AC</td>
    <td>172</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>连接线内阻 9CellConWireRes9</td>
    <td>u&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00B0</td>
    <td>176</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>连接线内阻 10CellConWireRes10</td>
    <td>u&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00B4</td>
    <td>180</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>连接线内阻 11CellConWireRes11</td>
    <td>u&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00B8</td>
    <td>184</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>连接线内阻 12CellConWireRes12</td>
    <td>u&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00BC</td>
    <td>188</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>连接线内阻 13CellConWireRes13</td>
    <td>u&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00C0</td>
    <td>192</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>连接线内阻 14CellConWireRes14</td>
    <td>u&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00C4</td>
    <td>196</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>连接线内阻 15CellConWireRes15</td>
    <td>u&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00C8</td>
    <td>200</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>连接线内阻 16CellConWireRes16</td>
    <td>u&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00CC</td>
    <td>204</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>连接线内阻 17CellConWireRes17</td>
    <td>u&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00D0</td>
    <td>208</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>连接线内阻 18CellConWireRes18</td>
    <td>u&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00D4</td>
    <td>212</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>连接线内阻 19CellConWireRes19</td>
    <td>u&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td rowspan="11">0x1000</td>
    <td>0x00D8</td>
    <td>216</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>连接线内阻 20CellConWireRes20</td>
    <td>u&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00DC</td>
    <td>220</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>连接线内阻 21CellConWireRes21</td>
    <td>u&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00E0</td>
    <td>224</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>连接线内阻 22CellConWireRes22</td>
    <td>u&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00E4</td>
    <td>228</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>连接线内阻 23CellConWireRes23</td>
    <td>u&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00E8</td>
    <td>232</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>连接线内阻 24CellConWireRes24</td>
    <td>u&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00EC</td>
    <td>236</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>连接线内阻 25CellConWireRes25</td>
    <td>u&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00F0</td>
    <td>240</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>连接线内阻 26CellConWireRes26</td>
    <td>u&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00F4</td>
    <td>244</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>连接线内阻 27CellConWireRes27</td>
    <td>u&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00F8</td>
    <td>248</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>连接线内阻 28CellConWireRes28</td>
    <td>u&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00FC</td>
    <td>252</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>连接线内阻 29CellConWireRes29</td>
    <td>u&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0100</td>
    <td>256</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>连接线内阻 30CellConWireRes30</td>
    <td>u&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x0104</td>
    <td>260</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>连接线内阻 31CellConWireRes31</td>
    <td>u&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td rowspan="13">0x1000</td>
    <td>0x0108</td>
    <td>264</td>
    <td>UINT32</td>
    <td>4</td>
    <td>RW</td>
    <td>设备地址 DevAdd</td>
    <td>H</td>
    <td></td>
  </tr>
  <tr>
    <td>0x010C</td>
    <td>268</td>
    <td>UINT32</td>
    <td>4</td>
    <td>RW</td>
    <td>预充延时 TIMPrecharge</td>
    <td>S</td>
    <td></td>
  </tr>
  <tr>
    <td rowspan="10">0x0114</td>
    <td rowspan="10">276</td>
    <td rowspan="10">UINT16</td>
    <td rowspan="10">2</td>
    <td>RW</td>
    <td>加热使能 HeatEN</td>
    <td></td>
    <td>1: 打开; 0: 关闭 (BIT0)</td>
  </tr>
  <tr>
    <td>RW</td>
    <td>温度传感器禁用 Disable-temp-sensor</td>
    <td></td>
    <td>1: 打开; 0: 关闭 (BIT1)</td>
  </tr>
  <tr>
    <td>RW</td>
    <td>GPS 心跳包 GPS Heartbeat</td>
    <td></td>
    <td>1: 打开; 0: 关闭 (BIT2)</td>
  </tr>
  <tr>
    <td>RW</td>
    <td>电源端口切换 Port Switch</td>
    <td></td>
    <td>1: RS485; 0: CAN (BIT3)</td>
  </tr>
  <tr>
    <td>RW</td>
    <td>显示屏常亮 LCD Always On</td>
    <td></td>
    <td>1: 打开; 0: 关闭 (BIT4)</td>
  </tr>
  <tr>
    <td>RW</td>
    <td>外部充电器 External Charger</td>
    <td></td>
    <td>1: 打开; 0: 关闭 (BIT5)</td>
  </tr>
  <tr>
    <td>RW</td>
    <td>智能休眠 SmartSleep</td>
    <td></td>
    <td>1: 打开; 0: 关闭 (BIT6)</td>
  </tr>
  <tr>
    <td>RW</td>
    <td>禁用显示模块 DisablePCLModule</td>
    <td></td>
    <td>1: 打开; 0: 关闭 (BIT7)</td>
  </tr>
  <tr>
    <td>RW</td>
    <td>禁用存储数据 DisableStoredData</td>
    <td></td>
    <td>1: 打开; 0: 关闭 (BIT8)</td>
  </tr>
  <tr>
    <td>RW</td>
    <td>充电浮充模式 ChargingFloatMode</td>
    <td></td>
    <td>1: 打开; 0: 关闭 (BIT9)</td>
  </tr>
  <tr>
    <td>0x0118</td>
    <td>280</td>
    <td>UINT8</td>
    <td></td>
    <td>RW</td>
    <td>智能休眠时间 TIMSmartSleep</td>
    <td>H</td>
    <td></td>
  </tr>
  <tr>
    <td rowspan="21">0x0000</td>
    <td>0x0000</td>
    <td>0</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>第1节电池 1CellVol1</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0002</td>
    <td>2</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>第2节电池 2CellVol2</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0004</td>
    <td>4</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>第3节电池 3CellVol3</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0006</td>
    <td>6</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>第4节电池 4CellVol4</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0008</td>
    <td>8</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>第5节电池 5CellVol5</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x000A</td>
    <td>10</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>第6节电池 6CellVol6</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x000C</td>
    <td>12</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>第7节电池 7CellVol7</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x000E</td>
    <td>14</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>第8节电池 8CellVol8</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0010</td>
    <td>16</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>第9节电池 9CellVol9</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0012</td>
    <td>18</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>第10节电池 10CellVol10</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0014</td>
    <td>20</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>第11节电池 11CellVol11</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0016</td>
    <td>22</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>第12节电池 12CellVol12</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0018</td>
    <td>24</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>第13节电池 13CellVol13</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x001A</td>
    <td>26</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>第14节电池 14CellVol14</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x001C</td>
    <td>28</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>第15节电池 15CellVol15</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x001E</td>
    <td>30</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>第16节电池 16CellVol16</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0020</td>
    <td>32</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>第17节电池 17CellVol17</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0022</td>
    <td>34</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>第18节电池 18CellVol18</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0024</td>
    <td>36</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>第19节电池 19CellVol19</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0026</td>
    <td>38</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>第20节电池 20CellVol20</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0028</td>
    <td>40</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>第21节电池 21CellVol21</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td rowspan="36">0x0000</td>
    <td>0x002A</td>
    <td>42</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>第22节电池 22CellVol22</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x002C</td>
    <td>44</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>第23节电池 23CellVol23</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x002E</td>
    <td>46</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>第24节电池 24CellVol24</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0030</td>
    <td>48</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>第25节电池 25CellVol25</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0032</td>
    <td>50</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>第26节电池 26CellVol26</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0034</td>
    <td>52</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>第27节电池 27CellVol27</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0036</td>
    <td>54</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>第28节电池 28CellVol28</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0038</td>
    <td>56</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>第29节电池 29CellVol29</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x003A</td>
    <td>58</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>第30节电池 30CellVol30</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x003C</td>
    <td>60</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>第31节电池 31CellVol31</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x003E</td>
    <td>62</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>第32节电池 32CellVol32</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0040</td>
    <td>64</td>
    <td>UINT32</td>
    <td>4</td>
    <td>R</td>
    <td>均衡状态 CellSta</td>
    <td></td>
    <td>BIT[n]为1表示该电池在均衡</td>
  </tr>
  <tr>
    <td>0x0044</td>
    <td>68</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>平均电压 VolCellVolAve</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0046</td>
    <td>70</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>最大电压 VolCellVolMax</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0048</td>
    <td>72</td>
    <td>UINT8</td>
    <td rowspan="2">2</td>
    <td>R</td>
    <td>最大电压电池编号 MaxVolCellNbr</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>0x0049</td>
    <td>73</td>
    <td>UINT8</td>
    <td>R</td>
    <td>最小电压电池编号 MinVolCellNbr</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>0x004A</td>
    <td>74</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>连接线内阻 0CellConWireRes0</td>
    <td>m&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x004C</td>
    <td>76</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>连接线内阻 1CellConWireRes1</td>
    <td>m&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x004E</td>
    <td>78</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>连接线内阻 2CellConWireRes2</td>
    <td>m&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0050</td>
    <td>80</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>连接线内阻 3CellConWireRes3</td>
    <td>m&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0052</td>
    <td>82</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>连接线内阻 4CellConWireRes4</td>
    <td>m&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0054</td>
    <td>84</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>连接线内阻 5CellConWireRes5</td>
    <td>m&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0056</td>
    <td>86</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>连接线内阻 6CellConWireRes6</td>
    <td>m&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0058</td>
    <td>88</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>连接线内阻 7CellConWireRes7</td>
    <td>m&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x005A</td>
    <td>90</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>连接线内阻 8CellConWireRes8</td>
    <td>m&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x005C</td>
    <td>92</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>连接线内阻 9CellConWireRes9</td>
    <td>m&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x005E</td>
    <td>94</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>连接线内阻 10CellConWireRes10</td>
    <td>m&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0060</td>
    <td>96</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>连接线内阻 11CellConWireRes11</td>
    <td>m&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0062</td>
    <td>98</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>连接线内阻 12CellConWireRes12</td>
    <td>m&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0064</td>
    <td>100</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>连接线内阻 13CellConWireRes13</td>
    <td>m&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0066</td>
    <td>102</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>连接线内阻 14CellConWireRes14</td>
    <td>m&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0068</td>
    <td>104</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>连接线内阻 15CellConWireRes15</td>
    <td>m&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x006A</td>
    <td>106</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>连接线内阻 16CellConWireRes16</td>
    <td>m&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x006C</td>
    <td>108</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>连接线内阻 17CellConWireRes17</td>
    <td>m&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x006E</td>
    <td>110</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>连接线内阻 18CellConWireRes18</td>
    <td>m&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0070</td>
    <td>112</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>连接线内阻 19CellConWireRes19</td>
    <td>m&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td rowspan="13">0x0000</td>
    <td>0x0072</td>
    <td>114</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>连接线内阻 20CellConWireRes20</td>
    <td>m&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0074</td>
    <td>116</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>连接线内阻 21CellConWireRes21</td>
    <td>m&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0076</td>
    <td>118</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>连接线内阻 22CellConWireRes22</td>
    <td>m&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0078</td>
    <td>120</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>连接线内阻 23CellConWireRes23</td>
    <td>m&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x007A</td>
    <td>122</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>连接线内阻 24CellConWireRes24</td>
    <td>m&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x007C</td>
    <td>124</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>连接线内阻 25CellConWireRes25</td>
    <td>m&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x007E</td>
    <td>126</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>连接线内阻 26CellConWireRes26</td>
    <td>m&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0080</td>
    <td>128</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>连接线内阻 27CellConWireRes27</td>
    <td>m&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0082</td>
    <td>130</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>连接线内阻 28CellConWireRes28</td>
    <td>m&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0084</td>
    <td>132</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>连接线内阻 29CellConWireRes29</td>
    <td>m&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0086</td>
    <td>134</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>连接线内阻 30CellConWireRes30</td>
    <td>m&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0088</td>
    <td>136</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>连接线内阻 31CellConWireRes31</td>
    <td>m&Omega;</td>
    <td></td>
  </tr>
  <tr>
    <td>0x008A</td>
    <td>138</td>
    <td>INT16</td>
    <td>2</td>
    <td>R</td>
    <td>MOS管温度 TempMos</td>
    <td>0.1&deg;C</td>
    <td></td>
  </tr>
  <tr>
    <td rowspan="4">0x1200</td>
    <td>0x008C</td>
    <td>140</td>
    <td>UINT32</td>
    <td>4</td>
    <td>R</td>
    <td>连接线内阻状态 WireResSta</td>
    <td></td>
    <td>BIT[n]为1表示该连接线断路</td>
  </tr>
  <tr>
    <td>0x0090</td>
    <td>144</td>
    <td>UINT32</td>
    <td>4</td>
    <td>R</td>
    <td>电池组总电压 BatVol</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0094</td>
    <td>148</td>
    <td>UINT32</td>
    <td>4</td>
    <td>R</td>
    <td>电池功率 BatWatt</td>
    <td>mW</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0098</td>
    <td>152</td>
    <td>INT32</td>
    <td>4</td>
    <td>R</td>
    <td>电池电流 BatCur</td>
    <td>mA</td>
    <td></td>
  </tr>
  <tr>
    <td rowspan="22">0x0000</td>
    <td>0x009C</td>
    <td>156</td>
    <td>INT16</td>
    <td>2</td>
    <td>R</td>
    <td>电池温度 TempBat 1</td>
    <td>0.1&deg;C</td>
    <td></td>
  </tr>
  <tr>
    <td>0x009E</td>
    <td>158</td>
    <td>INT16</td>
    <td>2</td>
    <td>R</td>
    <td>电池温度 TempBat 2</td>
    <td>0.1&deg;C</td>
    <td></td>
  </tr>
  <tr>
    <td rowspan="20">0x00A0</td>
    <td rowspan="20">160</td>
    <td rowspan="20">UINT32</td>
    <td rowspan="20">4</td>
    <td rowspan="20">R</td>
    <td>电池短路保护 AlarmBatSCP</td>
    <td></td>
    <td>1: 故障; 0: 正常 (BIT0)</td>
  </tr>
  <tr>
    <td>MOS过温保护 AlarmMosOTP</td>
    <td></td>
    <td>1: 故障; 0: 正常 (BIT1)</td>
  </tr>
  <tr>
    <td>三元锂与磷酸铁锂不匹配 AlarmCellQuantity</td>
    <td></td>
    <td>1: 故障; 0: 正常 (BIT2)</td>
  </tr>
  <tr>
    <td>单体过压保护 AlarmCellOVP</td>
    <td></td>
    <td>1: 故障; 0: 正常 (BIT3)</td>
  </tr>
  <tr>
    <td>单体欠压保护 AlarmCellUVP</td>
    <td></td>
    <td>1: 故障; 0: 正常 (BIT4)</td>
  </tr>
  <tr>
    <td>整组过压保护 AlarmBatOVP</td>
    <td></td>
    <td>1: 故障; 0: 正常 (BIT5)</td>
  </tr>
  <tr>
    <td>整组欠压保护 AlarmBatUVP</td>
    <td></td>
    <td>1: 故障; 0: 正常 (BIT6)</td>
  </tr>
  <tr>
    <td>充电过流保护 AlarmBatOCC</td>
    <td></td>
    <td>1: 故障; 0: 正常 (BIT7)</td>
  </tr>
  <tr>
    <td>放电过流保护 AlarmBatOCP</td>
    <td></td>
    <td>1: 故障; 0: 正常 (BIT8)</td>
  </tr>
  <tr>
    <td>充电过温保护 AlarmBatCOT</td>
    <td></td>
    <td>1: 故障; 0: 正常 (BIT9)</td>
  </tr>
  <tr>
    <td>辅助CPU通讯故障 AlarmCPUAuxCommErr</td>
    <td></td>
    <td>1: 故障; 0: 正常 (BIT10)</td>
  </tr>
  <tr>
    <td>单体欠压保护 AlarmCellUVP</td>
    <td></td>
    <td>1: 故障; 0: 正常 (BIT11)</td>
  </tr>
  <tr>
    <td>整组过压保护 AlarmBatOVP</td>
    <td></td>
    <td>1: 故障; 0: 正常 (BIT12)</td>
  </tr>
  <tr>
    <td>整组欠压保护 AlarmBatUVP</td>
    <td></td>
    <td>1: 故障; 0: 正常 (BIT13)</td>
  </tr>
  <tr>
    <td>充电过流保护 AlarmBatOCC</td>
    <td></td>
    <td>1: 故障; 0: 正常 (BIT14)</td>
  </tr>
  <tr>
    <td>放电过流保护 AlarmBatOCP</td>
    <td></td>
    <td>1: 故障; 0: 正常 (BIT15)</td>
  </tr>
  <tr>
    <td>充电低温保护 AlarmBatCUT</td>
    <td></td>
    <td>1: 故障; 0: 正常 (BIT16)</td>
  </tr>
  <tr>
    <td>放电过温保护 AlarmBatDOT</td>
    <td></td>
    <td>1: 故障; 0: 正常 (BIT17)</td>
  </tr>
  <tr>
    <td>GPS断开连接 GPSDisconnected</td>
    <td></td>
    <td>1: 故障; 0: 正常 (BIT18)</td>
  </tr>
  <tr>
    <td>修改密码失败 Modify PWD failure</td>
    <td></td>
    <td>1: 故障; 0: 正常 (BIT19)</td>
  </tr>
  <tr>
    <td rowspan="13">0x0000</td>
    <td rowspan="4">0x00A0</td>
    <td rowspan="4">160</td>
    <td rowspan="4">UINT32</td>
    <td rowspan="4">4</td>
    <td rowspan="4">R</td>
    <td>放电开启失败 Discharge On Failed</td>
    <td></td>
    <td>1: 故障; 0: 正常 (BIT20)</td>
  </tr>
  <tr>
    <td>电池温度传感器异常 Battery Over Temp alarm</td>
    <td></td>
    <td>1: 故障; 0: 正常 (BIT21)</td>
  </tr>
  <tr>
    <td>电池温度传感器异常 Temperature sensor anomaly</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>并机模块故障 PCLModule anomaly</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>0x00A4</td>
    <td>164</td>
    <td>INT16</td>
    <td>2</td>
    <td>R</td>
    <td>均衡电流 BalanCurrent</td>
    <td>mA</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00A6</td>
    <td>166</td>
    <td>UINT8</td>
    <td rowspan="2">2</td>
    <td>R</td>
    <td>电池状态 BatSta</td>
    <td></td>
    <td>2: 放电; 1: 充电; 0: 关闭</td>
  </tr>
  <tr>
    <td></td>
    <td></td>
    <td>UINT8</td>
    <td>R</td>
    <td>剩余电量 SOCStateOfCharge</td>
    <td>%</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00A8</td>
    <td>168</td>
    <td>INT32</td>
    <td>4</td>
    <td>R</td>
    <td>剩余容量 SOCCapRemain</td>
    <td>mAH</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00AC</td>
    <td>172</td>
    <td>UINT32</td>
    <td>4</td>
    <td>R</td>
    <td>电池实际容量 SOCFullChargeCap</td>
    <td>mAH</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00B0</td>
    <td>176</td>
    <td>UINT32</td>
    <td>4</td>
    <td>R</td>
    <td>循环次数 SOCCycleCount</td>
    <td>次</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00B4</td>
    <td>180</td>
    <td>UINT32</td>
    <td>4</td>
    <td>R</td>
    <td>循环总容量 SOCCycleCap</td>
    <td>mAH</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00B8</td>
    <td>184</td>
    <td>UINT8</td>
    <td rowspan="2">2</td>
    <td>R</td>
    <td>健康度 SOH</td>
    <td>%</td>
    <td></td>
  </tr>
  <tr>
    <td></td>
    <td></td>
    <td>UINT8</td>
    <td>R</td>
    <td>预充状态 Precharge</td>
    <td></td>
    <td>1: 打开; 0: 关闭</td>
  </tr>
  <tr>
    <td rowspan="11">0x0000</td>
    <td>0x00BA</td>
    <td>186</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>用户报警值 UserAlarm</td>
    <td>%</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00BC</td>
    <td>188</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>运行时间 RunTime</td>
    <td>S</td>
    <td></td>
  </tr>
  <tr>
    <td rowspan="2">0x00C0</td>
    <td rowspan="2">192</td>
    <td>UINT8</td>
    <td rowspan="2">2</td>
    <td>R</td>
    <td>充电状态 Charge</td>
    <td></td>
    <td>1: 打开; 0: 关闭</td>
  </tr>
  <tr>
    <td>UINT8</td>
    <td>R</td>
    <td>放电状态 Discharge</td>
    <td></td>
    <td>1: 打开; 0: 关闭</td>
  </tr>
  <tr>
    <td>0x00C2</td>
    <td>194</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>用户报警值 2 UserAlarm2</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>0x00C4</td>
    <td>196</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>放电过流保护延时时间 TimeDeOCPR</td>
    <td>S</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00C6</td>
    <td>198</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>放电过流保护延时时间 TimeDeSCPR</td>
    <td>S</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00C8</td>
    <td>200</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>充电过流保护延时时间 TimeChOCPR</td>
    <td>S</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00CA</td>
    <td>202</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>充电过流保护延时时间 TimeChUVPR</td>
    <td>S</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00CC</td>
    <td>204</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>单体欠压保护延时时间 TimeUVP R</td>
    <td>S</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00CE</td>
    <td>206</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>单体过压保护延时时间 TimeOVPR</td>
    <td>S</td>
    <td></td>
  </tr>
  <tr>
    <td rowspan="6">0x0000</td>
    <td rowspan="6">0x00D0</td>
    <td rowspan="6">208</td>
    <td rowspan="6">UINT8</td>
    <td rowspan="6">2</td>
    <td rowspan="6">R</td>
    <td>MOS温度传感器缺失 MOS TempSensorAbsent</td>
    <td></td>
    <td>1: 正常; 0: 缺失 (BIT0)</td>
  </tr>
  <tr>
    <td>电池温度传感器1缺失 1 BatTempSensor1Absent</td>
    <td></td>
    <td>1: 正常; 0: 缺失 (BIT1)</td>
  </tr>
  <tr>
    <td>电池温度传感器2缺失 2 BatTempSensor2Absent</td>
    <td></td>
    <td>1: 正常; 0: 缺失 (BIT2)</td>
  </tr>
  <tr>
    <td>电池温度传感器3缺失 3 BatTempSensor3Absent</td>
    <td></td>
    <td>1: 正常; 0: 缺失 (BIT3)</td>
  </tr>
  <tr>
    <td>电池温度传感器4缺失 4 BatTempSensor4Absent</td>
    <td></td>
    <td>1: 正常; 0: 缺失 (BIT4)</td>
  </tr>
  <tr>
    <td>电池温度传感器5缺失 5 BatTempSensor5Absent</td>
    <td></td>
    <td>1: 正常; 0: 缺失 (BIT5)</td>
  </tr>
  <tr>
    <td rowspan="15">0x0000</td>
    <td></td>
    <td></td>
    <td>UINT8</td>
    <td></td>
    <td>R</td>
    <td>加热状态 Heating</td>
    <td></td>
    <td>1: 打开; 0: 关闭</td>
  </tr>
  <tr>
    <td>0x00D2</td>
    <td>210</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>Reserved</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>0x00D4</td>
    <td>212</td>
    <td>UINT16</td>
    <td>2</td>
    <td>RW</td>
    <td>应急开关时间 TimeEmergency</td>
    <td>S</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00D6</td>
    <td>214</td>
    <td>UINT16</td>
    <td>2</td>
    <td>RW</td>
    <td>放电过流保护释放电压 VolBatCurCorrect</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00D8</td>
    <td>216</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>充电过流保护释放电压 VolChargeCur</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00DA</td>
    <td>218</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>单体过压保护释放电压 VolDischargeCur</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00DC</td>
    <td>220</td>
    <td>FLOAT</td>
    <td>4</td>
    <td>RW</td>
    <td>电池电压校准因子 BatVolCorrect</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>0x00E4</td>
    <td>228</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>电池电压 BatVol</td>
    <td>0.01V</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00E6</td>
    <td>230</td>
    <td>INT16</td>
    <td>2</td>
    <td>R</td>
    <td>加热电流 HeatCurrent</td>
    <td>mA</td>
    <td></td>
  </tr>
  <tr>
    <td rowspan="2">0x00EE</td>
    <td rowspan="2">238</td>
    <td>UINT8</td>
    <td rowspan="2">2</td>
    <td>R</td>
    <td>Reserved</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>UINT8</td>
    <td>R</td>
    <td>充电器插入状态 ChargerPlugged</td>
    <td></td>
    <td>1: 插入; 0: 未插入</td>
  </tr>
  <tr>
    <td>0x00F0</td>
    <td>240</td>
    <td>UINT32</td>
    <td>4</td>
    <td>R</td>
    <td>系统运行时间 SysRunTicks</td>
    <td>0.1S</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00F8</td>
    <td>248</td>
    <td>INT16</td>
    <td>2</td>
    <td>R</td>
    <td>电池温度 TempBat 3</td>
    <td>0.1&deg;C</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00FA</td>
    <td>250</td>
    <td>INT16</td>
    <td>2</td>
    <td>R</td>
    <td>电池温度 TempBat 4</td>
    <td>0.1&deg;C</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00FC</td>
    <td>252</td>
    <td>INT16</td>
    <td>2</td>
    <td>R</td>
    <td>电池温度 TempBat 5</td>
    <td>0.1&deg;C</td>
    <td></td>
  </tr>
  <tr>
    <td rowspan="17">0x1400</td>
    <td>0x0100</td>
    <td>256</td>
    <td>UINT32</td>
    <td>4</td>
    <td>R</td>
    <td>RTC 时间戳 RTC Time</td>
    <td>S</td>
    <td>自2020-1-1开始计算</td>
  </tr>
  <tr>
    <td>0x0108</td>
    <td>264</td>
    <td>UINT32</td>
    <td>4</td>
    <td>R</td>
    <td>进入休眠时间 TimeEnterSleep</td>
    <td>S</td>
    <td></td>
  </tr>
  <tr>
    <td>0x010C</td>
    <td>268</td>
    <td>UINT16</td>
    <td>2</td>
    <td>RW</td>
    <td>并机模块电源保持使能 PCLModuleSta</td>
    <td></td>
    <td>1: 打开; 0: 关闭</td>
  </tr>
  <tr>
    <td>0x0000</td>
    <td>0</td>
    <td>ASCII</td>
    <td>16</td>
    <td>R</td>
    <td>厂家型号 ManufacturerDeviceID</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>0x0010</td>
    <td>16</td>
    <td>ASCII</td>
    <td>8</td>
    <td>R</td>
    <td>硬件版本 HardwareVersion</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>0x0018</td>
    <td>24</td>
    <td>ASCII</td>
    <td>8</td>
    <td>R</td>
    <td>软件版本 SoftwareVersion</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>0x0020</td>
    <td>32</td>
    <td>UINT32</td>
    <td>4</td>
    <td>R</td>
    <td>累计运行时间 MODRunTime</td>
    <td>S</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0024</td>
    <td>36</td>
    <td>UINT32</td>
    <td>4</td>
    <td>R</td>
    <td>上电次数 PWROnTimes</td>
    <td>次</td>
    <td></td>
  </tr>
  <tr>
    <td>0x00BC</td>
    <td>188</td>
    <td>UINT16</td>
    <td>2</td>
    <td>RW</td>
    <td>CAN 端口 1 使能 UART1MPRTOL Nbr</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>0x00B2</td>
    <td>178</td>
    <td>UINT8</td>
    <td></td>
    <td>RW</td>
    <td>CAN 端口 1 CANMPRTOL Nbr</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>0x00B4</td>
    <td>180</td>
    <td>UINT16</td>
    <td>16</td>
    <td>R</td>
    <td>串口 1 协议使能 UART1MPRTOL Enable</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>0x00C4</td>
    <td>196</td>
    <td>UINT16</td>
    <td>16</td>
    <td>R</td>
    <td>CAN 协议使能 CANMPRTOL Enable[0-15]</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>0x00D4</td>
    <td>212</td>
    <td>UINT8</td>
    <td rowspan="2">2</td>
    <td>RW</td>
    <td>串口 2 协议使能 UART2MPRTOL Nbr</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td></td>
    <td></td>
    <td>UINT8</td>
    <td>R</td>
    <td>串口 2 协议使能 UART2MPRTOL Enable[0]</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>0x00E4</td>
    <td>228</td>
    <td>UINT8</td>
    <td rowspan="2">2</td>
    <td>RW</td>
    <td>LCD 屏幕触发使能 LCD BuzzerTrigger</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td></td>
    <td></td>
    <td>UINT8</td>
    <td>R</td>
    <td>二号干接点触发 DRY2Trigger</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>0x00E6</td>
    <td>230</td>
    <td>UINT8</td>
    <td rowspan="2">2</td>
    <td>RW</td>
    <td>二号干接点触发 DRY2Trigger</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td rowspan="10">0x1400</td>
    <td>0x00E7</td>
    <td>231</td>
    <td>UINT8</td>
    <td>R</td>
    <td>UART1 协议使能 UART1MPRTOL Ver</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>0x00E8</td>
    <td>232</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>LCD 蜂鸣器触发阈值 LCDBuzzerTriggerVal</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>0x00EC</td>
    <td>236</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>LCD 蜂鸣器释放阈值 LCDBuzzerReleaseVal</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>0x00F0</td>
    <td>240</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>一号干接点触发 DRY1Trigger</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>0x00F4</td>
    <td>244</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>一号干接点释放 DRY1TriggerVal</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>0x00F8</td>
    <td>248</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>二号干接点触发 DRY2TriggerVal</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>0x00FC</td>
    <td>252</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>二号干接点释放 DRY2TriggerVal</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>0x0100</td>
    <td>256</td>
    <td>INT32</td>
    <td>4</td>
    <td>RW</td>
    <td>数据存储周期 DataStoredPeriod</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>0x0104</td>
    <td>260</td>
    <td>UINT8</td>
    <td rowspan="2">2</td>
    <td>RW</td>
    <td>接收超时时间 RCVTime</td>
    <td>0.1H</td>
    <td></td>
  </tr>
  <tr>
    <td></td>
    <td></td>
    <td>UINT8</td>
    <td>R</td>
    <td>发送超时时间 RPVTime</td>
    <td>0.1H</td>
    <td></td>
  </tr>
  <tr>
    <td>0x1400</td>
    <td>0x0106</td>
    <td>262</td>
    <td>UINT16</td>
    <td>2</td>
    <td>R</td>
    <td>CAN 端口 1 协议版本 CANMPRTOL Ver</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td rowspan="10">0x1600</td>
    <td>0x0000</td>
    <td>0</td>
    <td>UINT16</td>
    <td>4</td>
    <td>W</td>
    <td>保留 RVD</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>0x0000</td>
    <td>0</td>
    <td>UINT16</td>
    <td>4</td>
    <td>W</td>
    <td>电压校准 VoltageCalibration</td>
    <td>mV</td>
    <td></td>
  </tr>
  <tr>
    <td>0x0004</td>
    <td>4</td>
    <td>UINT16</td>
    <td>2</td>
    <td>W</td>
    <td>保护关机 Shutdown</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>0x0006</td>
    <td>6</td>
    <td>UINT16</td>
    <td>4</td>
    <td>W</td>
    <td>电流校准 CurrentCalibration</td>
    <td>mA</td>
    <td></td>
  </tr>
  <tr>
    <td>0x000A</td>
    <td>10</td>
    <td>UINT16</td>
    <td>2</td>
    <td>W</td>
    <td>三元锂 LI-ION</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>0x000C</td>
    <td>12</td>
    <td>UINT16</td>
    <td>2</td>
    <td>W</td>
    <td>磷酸铁锂 LIFEPO4</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>0x000E</td>
    <td>14</td>
    <td>UINT16</td>
    <td>2</td>
    <td>W</td>
    <td>钛酸锂 LTO</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>0x0010</td>
    <td>16</td>
    <td>UINT16</td>
    <td>2</td>
    <td>W</td>
    <td>紧急启动 Emergency</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>0x0012</td>
    <td>18</td>
    <td>UINT16</td>
    <td>4</td>
    <td>W</td>
    <td>时间校准 TimeCalibration</td>
    <td></td>
    <td></td>
  </tr>
</table>

## 示例数据

<table>
  <tr>
    <th colspan="2">寄存器</th>
    <th colspan="2">数据</th>
    <th rowspan="2">寄存器定义</th>
    <th rowspan="2">设置数值</th>
    <th rowspan="2">发送指令</th>
    <th rowspan="2">接收响应</th>
  </tr>
  <tr>
    <th>基地址</th>
    <th>偏移</th>
    <th>类型</th>
    <th>长度</th>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x0000</td>
    <td>UINT32</td>
    <td>4</td>
    <td>进入休眠电压VolSmartSleep</td>
    <td>3.54</td>
    <td>01 10 10 00 00 02 04 00 00 0D D4 3A A0</td>
    <td>01 10 10 00 00 02 45 08</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x0004</td>
    <td>UINT32</td>
    <td>4</td>
    <td>单体欠压保护VolCellUV</td>
    <td>2.83</td>
    <td>01 10 10 04 00 02 04 00 00 0B 0E B9 68</td>
    <td>01 10 10 04 00 02 04 C9</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x0008</td>
    <td>UINT32</td>
    <td>4</td>
    <td>单体欠压保护恢复VolCellUVPR</td>
    <td>2.86</td>
    <td>01 10 10 08 00 02 04 00 00 0B 2C 39 24</td>
    <td>01 10 10 08 00 02 C4 CA</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x000C</td>
    <td>UINT32</td>
    <td>4</td>
    <td>单体过充保护VolCellOV</td>
    <td>4.3</td>
    <td>01 10 10 0C 00 02 04 00 00 10 CC 33 AF</td>
    <td>01 10 10 0C 00 02 85 0B</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x0010</td>
    <td>UINT32</td>
    <td>4</td>
    <td>单体过充保护恢复电压VolCellOVPR</td>
    <td>4.16</td>
    <td>01 10 10 10 00 02 04 00 00 10 40 33 53</td>
    <td>01 10 10 10 00 02 44 CD</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x0014</td>
    <td>UINT32</td>
    <td>4</td>
    <td>触发均衡压差VolBalanTrig</td>
    <td>0.003</td>
    <td>01 10 10 14 00 02 04 00 00 00 03 7E 91</td>
    <td>01 10 10 14 00 02 05 0C</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x0018</td>
    <td>UINT32</td>
    <td>4</td>
    <td>SOC-100%电压VolSOC100%</td>
    <td>4.17</td>
    <td>01 10 10 18 00 02 04 00 00 10 4A B2 F2</td>
    <td>01 10 10 18 00 02 C5 0F</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x001C</td>
    <td>UINT32</td>
    <td>4</td>
    <td>SOC-0%电压VolSOC0%</td>
    <td>2.85</td>
    <td>01 10 10 1C 00 02 04 00 00 0B 22 8B 1F</td>
    <td>01 10 10 1C 00 02 84 CE</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x0020</td>
    <td>UINT32</td>
    <td>4</td>
    <td>推荐充电电压VolCellRCV</td>
    <td>4.2</td>
    <td>01 10 10 20 00 02 04 00 00 10 68 30 59</td>
    <td>01 10 10 20 00 02 44 C2</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x0024</td>
    <td>UINT32</td>
    <td>4</td>
    <td>浮充电压VolCellRFV</td>
    <td>4.16</td>
    <td>01 10 10 24 00 02 04 00 00 10 40 31 B4</td>
    <td>01 10 10 24 00 02 05 03</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x0028</td>
    <td>UINT32</td>
    <td>4</td>
    <td>自动关机电压VolSysPwrOff</td>
    <td>2.7</td>
    <td>01 10 10 28 00 02 04 00 00 0A 8C 3A D4</td>
    <td>01 10 10 28 00 02 C5 00</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x002C</td>
    <td>UINT32</td>
    <td>4</td>
    <td>持续充电电流CurBatCOC</td>
    <td>30</td>
    <td>01 10 10 2C 00 02 04 00 00 75 30 1A A6</td>
    <td>01 10 10 2C 00 02 84 C1</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x0030</td>
    <td>UINT32</td>
    <td>4</td>
    <td>充电过流保护延迟TimBATCOCPDly</td>
    <td>10</td>
    <td>01 10 10 30 00 02 04 00 00 00 0A BD 7C</td>
    <td>01 10 10 30 00 02 45 07</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x0034</td>
    <td>UINT32</td>
    <td>4</td>
    <td>充电过流保护解除TimBATCOCPRDly</td>
    <td>40</td>
    <td>01 10 10 34 00 02 04 00 00 00 28 3C 96</td>
    <td>01 10 10 34 00 02 04 C6</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x0038</td>
    <td>UINT32</td>
    <td>4</td>
    <td>持续放电电流CurBatDcOC</td>
    <td>149</td>
    <td>01 10 10 38 00 02 04 00 00 02 46 08 AE BB</td>
    <td>01 10 10 38 00 02 C4 C5</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x003C</td>
    <td>UINT32</td>
    <td>4</td>
    <td>放电过流保护延迟TimBatDcOCPDly</td>
    <td>30</td>
    <td>01 10 10 3C 00 02 04 00 00 00 1E BD 26</td>
    <td>01 10 10 3C 00 02 85 04</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x0040</td>
    <td>UINT32</td>
    <td>4</td>
    <td>放电过流保护解除TimBatDcOCPRDly</td>
    <td>40</td>
    <td>01 10 10 40 00 02 04 00 00 00 28 3A 41</td>
    <td>01 10 10 40 00 02 44 DC</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x0044</td>
    <td>UINT32</td>
    <td>4</td>
    <td>短路保护解除TimBATSCPRDly</td>
    <td>6</td>
    <td>01 10 10 44 00 02 04 00 00 00 06 BB AE</td>
    <td>01 10 10 44 00 02 05 1D</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x0048</td>
    <td>UINT32</td>
    <td>4</td>
    <td>最大均衡电流CurBalanMax</td>
    <td>1</td>
    <td>01 10 10 48 00 02 04 00 00 03 E8 3B 47</td>
    <td>01 10 10 48 00 02 C5 1E</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x004C</td>
    <td>INT32</td>
    <td>4</td>
    <td>充电高温保护TMPBatCOT</td>
    <td>75</td>
    <td>01 10 10 4C 00 02 04 00 00 02 EE BB 26</td>
    <td>01 10 10 4C 00 02 84 DF</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x0050</td>
    <td>INT32</td>
    <td>4</td>
    <td>充电高温恢复TMPBatCOTPR</td>
    <td>65</td>
    <td>01 10 10 50 00 02 04 00 00 02 8A BB 94</td>
    <td>01 10 10 50 00 02 45 19</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x0054</td>
    <td>INT32</td>
    <td>4</td>
    <td>放电高温保护TMPBatDcOT</td>
    <td>75</td>
    <td>01 10 10 54 00 02 04 00 00 02 EE BB 8C</td>
    <td>01 10 10 54 00 02 04 D8</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x0058</td>
    <td>INT32</td>
    <td>4</td>
    <td>放电高温恢复TMPBatDcOTPR</td>
    <td>65</td>
    <td>01 10 10 58 00 02 04 00 00 02 8A BA 32</td>
    <td>01 10 10 58 00 02 C4 DB</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x005C</td>
    <td>INT32</td>
    <td>4</td>
    <td>充电低温保护TMPBATCUT</td>
    <td>-25</td>
    <td>01 10 10 5C 00 02 04 FF FF FF 06 FA D0</td>
    <td>01 10 10 5C 00 02 85 1A</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x0060</td>
    <td>INT32</td>
    <td>4</td>
    <td>充电低温恢复TMPBATCUTPR</td>
    <td>-15</td>
    <td>01 10 10 60 00 02 04 FF FF FF 6A F9 BC</td>
    <td>01 10 10 60 00 02 45 16</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x0064</td>
    <td>INT32</td>
    <td>4</td>
    <td>MOS过温保护TMPMosOT</td>
    <td>105</td>
    <td>01 10 10 64 00 02 04 00 00 04 1A BA BF</td>
    <td>01 10 10 64 00 02 04 D7</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x0068</td>
    <td>INT32</td>
    <td>4</td>
    <td>MOS过温保护恢复TMPMosOTPR</td>
    <td>90</td>
    <td>01 10 10 68 00 02 04 00 00 03 84 39 72</td>
    <td>01 10 10 68 00 02 C4 D4</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x006C</td>
    <td>UINT32</td>
    <td>4</td>
    <td>单体数量CellCount</td>
    <td>15</td>
    <td>01 10 10 6C 00 02 04 00 00 00 0F 78 16</td>
    <td>01 10 10 6C 00 02 85 15</td>
  </tr>
  <tr>
    <td rowspan="2">0x1000</td>
    <td rowspan="2">0x0070</td>
    <td rowspan="2">UINT32</td>
    <td rowspan="2">4</td>
    <td rowspan="2">充电开关BatChargeEN</td>
    <td>开:</td>
    <td>01 10 10 70 00 02 04 00 00 00 01 F8 8B</td>
    <td>01 10 10 70 00 02 44 D3</td>
  </tr>
  <tr>
    <td>关:</td>
    <td>01 10 10 70 00 02 04 00 00 00 00 39 4B</td>
    <td>01 10 10 70 00 02 44 D3</td>
  </tr>
  <tr>
    <td rowspan="2">0x1000</td>
    <td rowspan="2">0x0074</td>
    <td rowspan="2">UINT32</td>
    <td rowspan="2">4</td>
    <td rowspan="2">放电开关BatDisChargeEN</td>
    <td>开:</td>
    <td>01 10 10 74 00 02 04 00 00 00 01 F9 78</td>
    <td>01 10 10 74 00 02 05 12</td>
  </tr>
  <tr>
    <td>关:</td>
    <td>01 10 10 74 00 02 04 00 00 00 00 38 B8</td>
    <td>01 10 10 74 00 02 05 12</td>
  </tr>
  <tr>
    <td rowspan="2">0x1000</td>
    <td rowspan="2">0x0078</td>
    <td rowspan="2">UINT32</td>
    <td rowspan="2">4</td>
    <td rowspan="2">均衡开关BalanEN</td>
    <td>开:</td>
    <td>01 10 10 78 00 02 04 00 00 00 01 F9 2D</td>
    <td>01 10 16 20 00 01 04 4B</td>
  </tr>
  <tr>
    <td>关:</td>
    <td>01 10 10 78 00 02 04 00 00 00 00 38 ED</td>
    <td>01 10 16 20 00 01 04 4B</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x007C</td>
    <td>UINT32</td>
    <td>4</td>
    <td>电池设计容量CapBatCell</td>
    <td>50</td>
    <td>01 10 10 7C 00 02 04 00 00 C3 50 69 D2</td>
    <td>01 10 10 7C 00 02 84 D0</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x0080</td>
    <td>UINT32</td>
    <td>4</td>
    <td>短路保护延迟SCPDelay</td>
    <td>140</td>
    <td>01 10 10 80 00 02 04 00 00 00 8C 37 AA</td>
    <td>01 10 10 80 00 02 44 E0</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x0084</td>
    <td>UINT32</td>
    <td>4</td>
    <td>均衡起始电压VolStartBalan</td>
    <td>3.1</td>
    <td>01 10 10 84 00 02 04 00 00 0C 1C 33 35</td>
    <td>01 10 10 84 00 02 05 21</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x0088</td>
    <td>UINT32</td>
    <td>4</td>
    <td>连接线内阻0CellConWireRes0</td>
    <td>0.1</td>
    <td>01 10 10 88 00 02 04 00 00 00 64 36 42</td>
    <td>01 10 10 88 00 02 C5 22</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x008C</td>
    <td>UINT32</td>
    <td>4</td>
    <td>连接线内阻1CellConWireRes1</td>
    <td>0.1</td>
    <td>01 10 10 8C 00 02 04 00 00 00 64 37 B1</td>
    <td>01 10 10 8C 00 02 84 E3</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x0090</td>
    <td>UINT32</td>
    <td>4</td>
    <td>连接线内阻2CellConWireRes2</td>
    <td>0.1</td>
    <td>01 10 10 90 00 02 04 00 00 00 64 36 E8</td>
    <td>01 10 10 90 00 02 45 25</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x0094</td>
    <td>UINT32</td>
    <td>4</td>
    <td>连接线内阻3CellConWireRes3</td>
    <td>0.1</td>
    <td>01 10 10 94 00 02 04 00 00 00 64 37 1B</td>
    <td>01 10 10 94 00 02 04 E4</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x0098</td>
    <td>UINT32</td>
    <td>4</td>
    <td>连接线内阻4CellConWireRes4</td>
    <td>0.1</td>
    <td>01 10 10 98 00 02 04 00 00 00 64 37 4E</td>
    <td>01 10 10 98 00 02 C4 E7</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x009C</td>
    <td>UINT32</td>
    <td>4</td>
    <td>连接线内阻5CellConWireRes5</td>
    <td>0.1</td>
    <td>01 10 10 9C 00 02 04 00 00 00 64 36 BD</td>
    <td>01 10 10 9C 00 02 85 26</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x00A0</td>
    <td>UINT32</td>
    <td>4</td>
    <td>连接线内阻6CellConWireRes6</td>
    <td>0.1</td>
    <td>01 10 10 A0 00 02 04 00 00 00 64 35 FC</td>
    <td>01 10 10 A0 00 02 45 2A</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x00A4</td>
    <td>UINT32</td>
    <td>4</td>
    <td>连接线内阻7CellConWireRes7</td>
    <td>0.1</td>
    <td>01 10 10 A4 00 02 04 00 00 00 64 34 0F</td>
    <td>01 10 10 A4 00 02 04 EB</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x00A8</td>
    <td>UINT32</td>
    <td>4</td>
    <td>连接线内阻8CellConWireRes8</td>
    <td>0.1</td>
    <td>01 10 10 A8 00 02 04 00 00 00 64 34 5A</td>
    <td>01 10 10 A8 00 02 C4 E8</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x00AC</td>
    <td>UINT32</td>
    <td>4</td>
    <td>连接线内阻9CellConWireRes9</td>
    <td>0.1</td>
    <td>01 10 10 AC 00 02 04 00 00 00 64 35 A9</td>
    <td>01 10 10 AC 00 02 85 29</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x00B0</td>
    <td>UINT32</td>
    <td>4</td>
    <td>连接线内阻10CellConWireRes10</td>
    <td>0.1</td>
    <td>01 10 10 B0 00 02 04 00 00 00 64 34 F0</td>
    <td>01 10 10 B0 00 02 44 EF</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x00B4</td>
    <td>UINT32</td>
    <td>4</td>
    <td>连接线内阻11CellConWireRes11</td>
    <td>0.1</td>
    <td>01 10 10 B4 00 02 04 00 00 00 64 35 03</td>
    <td>01 10 10 B4 00 02 05 2E</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x00B8</td>
    <td>UINT32</td>
    <td>4</td>
    <td>连接线内阻12CellConWireRes12</td>
    <td>0.1</td>
    <td>01 10 10 B8 00 02 04 00 00 00 64 35 56</td>
    <td>01 10 10 B8 00 02 C5 2D</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x00BC</td>
    <td>UINT32</td>
    <td>4</td>
    <td>连接线内阻13CellConWireRes13</td>
    <td>0.1</td>
    <td>01 10 10 BC 00 02 04 00 00 00 64 34 A5</td>
    <td>01 10 10 BC 00 02 84 EC</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x00C0</td>
    <td>UINT32</td>
    <td>4</td>
    <td>连接线内阻14CellConWireRes14</td>
    <td>0.1</td>
    <td>01 10 10 C0 00 02 04 00 00 00 64 33 D4</td>
    <td>01 10 10 C0 00 02 45 34</td>
  </tr>
  <tr>
    <td>0x1000</td>
    <td>0x00C4</td>
    <td>UINT32</td>
    <td>4</td>
    <td>连接线内阻15CellConWireRes15</td>
    <td>0.1</td>
    <td>01 10 10 C4 00 02 04 00 00 00 64 32 27</td>
    <td>01 10 10 C4 00 02 04 F5</td>
  </tr>
</table>

成都极空科技有限公司

