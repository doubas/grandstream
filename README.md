# Grandstream UCM & VoIP Phone Controller Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)
[![Grandstream: UCM6300](https://img.shields.io/badge/Grandstream-UCM6300%20Series-red.svg)](https://www.grandstream.com/products/ip-pbxs/ucm-series)

A comprehensive AI agent skill and command-line automation toolkit for controlling **Grandstream UCM6300 Series IPPBX** systems (via the official HTTPS API) and programmatically provisioning **Grandstream GXP16xx Series IP Phones**.

---

## 🚀 Features

- **Cross-Platform Python CLI (`scripts/ucm_cli.py`)**: Seamlessly runs on Windows PowerShell, macOS, and Linux without external shell tools.
- **Challenge-Response HTTPS Authentication**: Implements Grandstream's 2-stage MD5 challenge-response handshake (`POST /api`) and manages authenticated session cookies.
- **Auto-Credential Phone Provisioning**: Single-command provisioning for GXP1628 phones (`provision-phone`) that queries the PBX directly for extension secrets and pushes P-values via the phone's web API.
- **Official 124-Action Catalog**: Detailed documentation and CLI execution support for all 124 Grandstream IPPBX HTTPS API actions.
- **Full Telephony Inspection**: Query system status, extension registration states, analog/VoIP trunks, call routing rules, and active channels.

---

## 📋 Compatibility

- **PBX Hardware**: Grandstream UCM6301, UCM6302, UCM6304, UCM6308, and UCM6300A Audio series.
- **PBX Firmware**: Tested on `1.0.33.x` (Core / Base `1.0.33.30`).
- **IP Phone Endpoints**: Grandstream GXP1610, GXP1615, GXP1620, GXP1625, GXP1628, and GXP21xx series.
- **Requirements**: Python 3.8+ with `requests` and `urllib3`.

---

## ⚙️ Environment Configuration

Copy `.env.example` to `.env` in your workspace root:

```ini
# Grandstream UCM PBX HTTPS API Endpoint
UCM_URL=https://192.168.1.10:8089/api
UCM_IP=192.168.1.10
UCM_PORT=8089

# HTTPS API User configured under Integrations > API Configuration > HTTPS API Settings
UCM_USERNAME=api_user
UCM_PASSWORD=your_ucm_api_password_here

# Default admin password for GXP IP phones
GXP_ADMIN_PASSWORD=admin
```

> [!CAUTION]
> Never commit your `.env` file to version control. Keep `.env` in `.gitignore`.

---

## 🛠️ CLI Usage & Quick Start

The main CLI tool is located at `scripts/ucm_cli.py`.

### 1. Check PBX Hardware & System Health
Queries model, serial number, MAC address, uptime, system time, and firmware:
```bash
python scripts/ucm_cli.py status
```
*Output:*
```
=== GRANDSTREAM UCM6304A SYSTEM STATUS ===
Model:           UCM6304A
Part Number:     966000XXXXX
Serial Number:   35C02XXXXX
MAC Address:     00:0B:82:XX:XX:XX
Firmware:        Core: 1.0.33.x | Base: 1.0.33.x
GS Wave:         1.0.33.x
Uptime:          4 days 01:37:41
System Time:     16-09-2026 09:13:54 UTC
```

### 2. List All Extensions & Registration States
Displays extension numbers, user full names, account types, and live status (`Idle`, `Unavailable`, `Ringing`, `Busy`):
```bash
python scripts/ucm_cli.py extensions
```

### 3. Retrieve Extension Credentials & SIP Secret
Fetches extension details and the live SIP password from the PBX:
```bash
python scripts/ucm_cli.py extension 1001
```

### 4. Provision a Grandstream IP Desk Phone
Automatically queries the PBX for extension credentials, logs into the phone, sets P-values (SIP server, extension, secret, LCD name, 802.1Q Voice VLAN tag, QoS priority, PC port untagged pass-through), and reboots:
```bash
python scripts/ucm_cli.py provision-phone --ip 192.168.1.102 --ext 1001 --reboot
```

### 5. Inspect Trunks & Routes
```bash
# List analog FXO and VoIP/SIP trunks
python scripts/ucm_cli.py trunks

# List inbound and outbound routes
python scripts/ucm_cli.py routes
```

### 6. Execute Arbitrary API Actions
Execute any action from the 124-action catalog:
```bash
python scripts/ucm_cli.py request listQueue
python scripts/ucm_cli.py request getQueueCalling '{"queue_id": "6500"}'
```

---

## 📚 References & Technical Guides

- [references/api-catalog.md](references/api-catalog.md): Complete catalog of all 124 official Grandstream HTTPS API actions, parameters, and return payloads.
- [references/gxp-pvalues.md](references/gxp-pvalues.md): Grandstream GXP1628 P-values dictionary, GWT web login API, and LCD display mode flags.
- [references/example-voip-inventory.md](references/example-voip-inventory.md): Reference VoIP deployment topology, extension assignments, patch panel ports, and MAC addresses.

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
