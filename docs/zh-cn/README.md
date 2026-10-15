# Gobel Power 电池 Home Assistant Add-on (支持 JK BMS, Pace BMS, TDT BMS)

[English](../../README.md) | [Deutsch](../de/README.md)

> **注意**：寻找 ioBroker 版本？请访问 [ioBroker Gobel BMS Monitor 适配器](https://github.com/fancyui/ioBroker.gobel-bms-monitor)。
>
> [!TIP]
> **寻找原生集成 (Integration) 版本？**  
> 我们推出了全新的 **[Gobel Power 电池 Home Assistant 原生集成](https://github.com/fancyui/Gobel-Battery-HA-Integration)** 的预发布测试版本 (Pre-release)！  
> 该集成直接运行于 Home Assistant 内部（无需配置 MQTT Broker），并且原生支持**多站点/多设备同时监控**（可同时独立连接并采集不同 IP 或串口的多个电池组）。欢迎下载测试并向我们反馈！

最强大的智能储能电池监控 Home Assistant 集成插件。此插件为运行 Pace BMS、JK BMS 或 TDT BMS 硬件 of LiFePO4 电池包提供稳定、实时的遥测数据记录 and 诊断功能。

通过使用 MQTT 等标准协议，无缝桥接您的太阳能储能系统 (ESS) 与您的家庭自动化网络，以实时监控电池健康状况、单体电池电压、充电状态 (SoC) 以及系统保护状态。

## 主要功能与特点：
* **多 BMS 兼容性：** 原生支持 Pace BMS、JK BMS（55AA 协议）和 TDT BMS（*注：TDT BMS 可能仅兼容特定版本，未来版本可能会移除兼容支持*）。
* **灵活的连接选项：** 支持通过 RS232-USB 转接线、RS232 转以太网、RS232 转 WiFi、RS485 转以太网或 RS485 转 WiFi 进行硬件连接。
* **详尽的遥测数据：** 实时跟踪充电状态 (SoC)、健康状态 (SoH)、总电压、电流、单体电池均衡状态、温度、告警和故障保护状态。
* **单线并联管理 (Master-Slave)：** 极大简化您的接线。直接连接到主机 (Master) BMS，即可自动发现并汇总所有并联从机 (Slave) 电池包的数据。
* **即插即用的 Home Assistant 设置：** 快速部署并自动生成直观的仪表盘，以进行实时能源监控。

## 相关文档与工具
<a href="https://www.gobelpower.com/introduction_f61.html">Gobel Power 电池 Home Assistant Addon 使用手册</a>  
<a href="https://www.gobelpower.com/ha_dashboard_ap46.html">在线 Home Assistant 仪表盘生成器</a>

## 仪表盘示例：

![image](https://www.gobelpower.com/images/github/dashboard-gobel-power-home-assistant-addon-1.webp)

## Pace BMS 接线与配置指南：
- **需要使用 RS232-WIFI/Ethernet 模块或 RS232-USB 转接线**
- **连接接口**：将 Home Assistant 连接至 Pace BMS 的 **RS232** 或 **WIFI** 接口。
- **主机 BMS**：连接必须接入到**主机 (Master) BMS** 上。
- **拨码开关设置**：请确保主机 BMS 的拨码开关（DIP switch）设置为 **1000**。

## JK BMS 接线与配置指南：
- **需要使用 RS485-WIFI/Ethernet 模块或 RS485-USB 转接线**
- **连接接口**：将 Home Assistant 连接至 JK BMS 的 **RS485B** 或 **RS485C** 接口。
- **主机 BMS**：连接必须接入到**主机 (Master) BMS** 上。
- **拨码开关设置**：请确保主机 BMS 的拨码开关（DIP switch）设置为 **0000**。

## 重要配置说明：
### MQTT 自动发现前缀（Discovery Prefix / `host_name`）
> [!IMPORTANT]
> **请务必在 Add-on 的配置（Configuration）中正确设置 MQTT Discovery Prefix（`host_name`）：**
>
> * **默认值**：`homeassistant`
> * **必须与 Home Assistant 保持一致**：此选项用于指定发布 MQTT 自动发现主题的前缀。必须与 Home Assistant 中 MQTT 集成的 **『自动发现前缀』 (Discovery prefix)** 保持完全一致（可前往 HA **设置** > **设备与服务** > **MQTT** > **配置** / **重新配置** 中查看，默认为 `homeassistant`）。
> * **避免误填系统主机名**：请**不要**将其填为主机的系统主机名（例如 `rpi5`、`homeassistant.local` 等）。如果前缀与 HA MQTT 集成的自动发现前缀不匹配，虽然 MQTT Broker 中能查看到数据，但 Home Assistant 将无法自动发现任何电池设备与实体传感器（参考 [Issue #79](https://github.com/fancyui/Gobel-Battery-HA-Addon/issues/79)）。

### TDT BMS 兼容性提示
> [!WARNING]
> **TDT BMS 兼容性说明**：TDT BMS 可能仅兼容特定硬件或固件版本。由于协议变动及维护原因，未来版本中可能会移除对 TDT BMS 的兼容支持。

## 安装步骤：
点击下方按钮将本插件仓库添加至您的 Home Assistant 中：

<a href="https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https://github.com/fancyui/Gobel-Battery-HA-Addon" rel="nofollow"><img src="https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg" alt="打开您的 Home Assistant 实例，并显示预填有特定仓库 URL 的添加加载项仓库对话框。" data-canonical-src="https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg" style="max-width: 100%;"></a>
