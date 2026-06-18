# Gobel Power Battery Home Assistant Add-on (JK BMS, Pace BMS, TDT BMS)

[English](../../README.md) | [简体中文](../zh-cn/README.md)

> **Hinweis**: Suchen Sie nach der ioBroker-Version? Besuchen Sie den [ioBroker Gobel BMS Monitor Adapter](https://github.com/fancyui/ioBroker.gobel-bms-monitor).
>
> [!TIP]
> **Suchen Sie nach der nativen Home Assistant Integration?**  
> Wir haben eine Vorabversion (Pre-release) der nativen **[Gobel Power Battery Home Assistant Integration](https://github.com/fancyui/Gobel-Battery-HA-Integration)** veröffentlicht!  
> Sie läuft direkt in Home Assistant (kein MQTT-Broker erforderlich) und unterstützt die **Multi-Site-Überwachung** (gleichzeitige Verbindung mit mehreren Batteriebänken über verschiedene IP-Adressen, Ports oder serielle Anschlüsse). Wir freuen uns auf Ihr Feedback und Ihre Testergebnisse!

Die ultimative Home Assistant-Integration für die intelligente Überwachung von Energiespeichern. Dieses Add-on bietet eine robuste Echtzeit-Datenprotokollierung und -Diagnose für Ihre LiFePO4-Batteriebänke mit Pace BMS-, JK BMS- oder TDT BMS-Hardware.

Verbinden Sie Ihr Solarenergiespeichersystem (ESS) nahtlos mit Ihrem Heimautomatisierungsnetzwerk über Standardprotokolle wie MQTT, um den Batteriezustand, die einzelnen Zellspannungen, den Ladezustand (SoC) und Systemschutzfunktionen zu überwachen.

## Hauptmerkmale & Funktionen:
* **Multi-BMS-Kompatibilität:** Native Unterstützung für Pace BMS, JK BMS (55AA-Protokoll) und TDT BMS.
* **Vielseitige Konnektivitätsoptionen:** Verbinden Sie Ihre Hardware über RS232-USB, RS232-zu-Ethernet, RS232-zu-WiFi, RS485-zu-Ethernet oder RS485-zu-WiFi.
* **Umfassende Telemetrie:** Verfolgt Ladezustand (SoC), Batteriezustand (SoH), Gesamtspannung, Strom, individuellen Zellenausgleich, Temperaturen, Warnungen und Fehlerschutzfunktionen.
* **Eine Verbindung für alle (Master-Slave):** Vereinfachen Sie Ihre Verkabelung. Verbinden Sie sich direkt mit dem Master-BMS, um automatisch alle parallel geschalteten Slave-Batteriepacks zu erkennen und deren Daten zu aggregieren.
* **Plug-and-Play Home Assistant-Einrichtung:** Schnelle Bereitstellung und automatische Generierung von Dashboards für die Echtzeit-Energieüberwachung.

## Dokumente & Werkzeuge
<a href="https://www.gobelpower.com/introduction_f61.html">Gobel Power Battery Home Assistant Addon Handbuch</a>  
<a href="https://www.gobelpower.com/ha_dashboard_ap46.html">Online Home Assistant Dashboard Generator</a>

## Dashboard-Beispiel:

![image](https://www.gobelpower.com/images/github/dashboard-gobel-power-home-assistant-addon-1.webp)

## Anschlussanleitung für Pace BMS:
- **RS232-WIFI/Ethernet-Modul oder RS232-USB-Kabel erforderlich**
- **Anschlussport**: Verbinden Sie Home Assistant mit der **RS232**- oder **WIFI**-Schnittstelle des Pace BMS.
- **Master-BMS**: Die Verbindung muss mit dem **Master-BMS** hergestellt werden.
- **DIP-Schalter-Einstellungen**: Stellen Sie sicher, dass die DIP-Schalter (Wahlschalter) des Master-BMS auf **1000** eingestellt sind.

## Anschlussanleitung für JK BMS:
- **RS485-WIFI/Ethernet-Modul oder RS485-USB-Kabel erforderlich**
- **Anschlussport**: Verbinden Sie Home Assistant mit der **RS485B**- oder **RS485C**-Schnittstelle des JK BMS.
- **Master-BMS**: Die Verbindung muss mit dem **Master-BMS** hergestellt werden.
- **DIP-Schalter-Einstellungen**: Stellen Sie sicher, dass die DIP-Schalter (Wahlschalter) des Master-BMS auf **0000** eingestellt sind.

## Installation:
Klicken Sie auf die Schaltfläche, um das Add-on zu Home Assistant hinzuzufügen

<a href="https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https://github.com/fancyui/Gobel-Battery-HA-Addon" rel="nofollow"><img src="https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg" alt="Öffnen Sie Ihre Home Assistant-Instanz und zeigen Sie den Dialog zum Hinzufügen von Add-on-Repositories mit einer vorab ausgefüllten Repository-URL an." data-canonical-src="https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg" style="max-width: 100%;"></a>
