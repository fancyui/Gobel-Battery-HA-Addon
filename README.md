---
description: 
---

# Gobel Power Battery Home Assistant Add-on (JK BMS, Pace BMS, TDT BMS)

The ultimate Home Assistant integration for smart energy storage monitoring. This add-on provides robust, real-time data logging and diagnostics for your LiFePO4 battery banks running Pace BMS, JK BMS, or TDT BMS hardware. 

Seamlessly bridge your solar energy storage system (ESS) with your home automation network using standard protocols like MQTT to monitor battery health, individual cell voltages, state of charge (SoC), and system protections.

## Key Features & Capabilities:
* **Multi-BMS Compatibility:** Native support for Pace BMS, JK BMS (55AA protocol), and TDT BMS.
* **Versatile Connectivity Options:** Connect your hardware via RS232-USB, RS232-to-Ethernet, RS232-to-WiFi, RS485-to-Ethernet, or RS485-to-WiFi.
* **Comprehensive Telemetry:** Tracks state of charge (SoC), state of health (SoH), total voltage, current, individual cell balancing, temperatures, warnings, and fault protections.
* **One Connection for All (Master-Slave):** Simplify your wiring. Connect directly to the Master BMS to automatically discover and aggregate data from all parallel-connected slave battery packs.
* **Plug-and-Play Home Assistant Setup:** Quickly deploy and generate automated dashboards for real-time energy tracking.

## Documents & Tools
<a href="https://www.gobelpower.com/introduction_f61.html">Gobel Power Battery Home Assistant Addon Manual</a>  
<a href="https://www.gobelpower.com/ha_dashboard_ap46.html">Online Home Assistant Dashboard Generator</a>

## Dashboard Example:

![image](https://www.gobelpower.com/images/github/dashboard-gobel-power-home-assistant-addon-1.webp)

## JK BMS Connection Instructions:
- **Connection Port**: Connect Home Assistant to the **RS485B** or **RS485C** interface of the JK BMS.
- **Master BMS**: The connection must be made to the **Master BMS**.
- **DIP Switch Settings**: Ensure the DIP switches (Dial) are set to **0000**.

## Installation:
Click the button to add the addon to Home Assistant
<a href="https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https://github.com/fancyui/Gobel-Battery-HA-Addon" rel="nofollow"><img src="https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg" alt="Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled." data-canonical-src="https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg" style="max-width: 100%;"></a>
