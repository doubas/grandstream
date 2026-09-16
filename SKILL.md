---
name: grandstream-controller
description: Control and automate Grandstream UCM6304A PBX via HTTPS API and provision GXP16xx IP phones. Use when querying extensions, SIP credentials, trunks, routes, system status, active calls, call queues, IVR, or when configuring/rebooting VoIP phones.
license: MIT
compatibility: Requires network access to UCM PBX (VLAN 20) and Python 3.8+ with requests.
metadata:
  author: Grandstream Automation
  version: "1.0"
---

# Grandstream PBX & VoIP Phone Controller Skill

This skill provides programmatic control and automation for Grandstream telephony infrastructure, specifically the **Grandstream UCM6300 Series IPPBX** and **Grandstream GXP16xx/GXP21xx Series Gigabit IP Phones**.

---

## 1. Environment & Architecture

All credentials and network targets are loaded automatically from `.env` in the workspace root:

```ini
UCM_URL=https://192.168.1.10:8089/api
UCM_IP=192.168.1.10
UCM_PORT=8089
UCM_USERNAME=api_user
UCM_PASSWORD=<api_password>
GXP_ADMIN_PASSWORD=admin
```

---

## 2. CLI Helper Tool (`scripts/ucm_cli.py`)

The primary tool for interacting with the Grandstream system is `scripts/ucm_cli.py`.

### Commands

```bash
# Check PBX health, hardware model, uptime, and firmware
python scripts/ucm_cli.py status

# List all extensions and their current registration state
python scripts/ucm_cli.py extensions

# Retrieve detailed SIP credentials (including live SIP secret) for an extension
python scripts/ucm_cli.py extension 1001

# Inspect analog (FXO) and VoIP/SIP trunks
python scripts/ucm_cli.py trunks

# Inspect inbound and outbound routing rules
python scripts/ucm_cli.py routes

# Automatically provision a GXP16xx IP phone
# (Pulls name and SIP secret automatically from UCM PBX, configures P-values, and triggers soft reboot)
python scripts/ucm_cli.py provision-phone --ip 192.168.1.102 --ext 1001 --reboot

# Execute any arbitrary action from the 124 official HTTPS actions catalog
python scripts/ucm_cli.py request listQueue
```

---

## 3. HTTPS API Authentication Workflow

The UCM PBX HTTPS API uses a challenge-response handshake over `POST https://<ucm-ip>:8089/api`:

1. **Challenge Request**:
   ```json
   {"request": {"action": "challenge", "user": "api_user", "version": "1.0"}}
   ```
2. **Token Generation**:
   Compute `MD5(challenge + password)` (hex digest).
3. **Login Request**:
   ```json
   {"request": {"action": "login", "user": "api_user", "token": "<md5_token>"}}
   ```
4. **Session Cookie**:
   PBX returns a session cookie (`sid...`) valid for 10 minutes.
5. **Subsequent API Calls**:
   Include `"cookie": "<cookie>"` in the request object.
6. **Logout**:
   Send `{"request": {"action": "logout", "cookie": "<cookie>"}}`.

---

## 4. GXP IP Phone Provisioning & P-Values

When provisioning GXP phones directly via their web API (`POST http://<phone_ip>/cgi-bin/api.values.post`):
- `P47 = <pbx_ip>` — Primary SIP Server (UCM PBX)
- `P35 = <extension>` — SIP User ID
- `P36 = <extension>` — Authenticate ID
- `P34 = <secret>` — Authenticate Password (queried from UCM)
- `P270 = <name>` — Line Key and Screen Label
- `P3 = <name>` — Display Name / Caller ID
- `P2380 = 0` — Account Display Mode (`0` = User Name `P270`, `1` = User ID `P35`)
- `P271 = 1` — Account 1 Active
- `P51 = 20` — 802.1Q Voice VLAN Tag
- `P87 = 6` — Voice 802.1p QoS Priority
- `P229 = 0` — PC Port VLAN Tag (Untagged pass-through for employee PC)

> [!CAUTION]
> Rebooting a phone (`GET http://<phone_ip>/cgi-bin/api-sys_operation?passcode=admin&request=REBOOT`) temporarily interrupts network connectivity on the phone's downstream PC port. Schedule reboots or defer them during active working sessions.

---

## 5. References

- [Full 124-Action HTTPS API Catalog](references/api-catalog.md)
- [GXP1628 P-Value Reference](references/gxp-pvalues.md)
- [Example VoIP & Extension Inventory](references/example-voip-inventory.md)
