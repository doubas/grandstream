# Example VoIP & Extension Inventory

This document provides a template reference for mapping VoIP extensions, switch ports, and IP phones.

---

## 1. System Overview (Example)

| Parameter | Configuration | Notes |
|---|---|---|
| **PBX Model** | Grandstream UCM6304A | Core PBX controller |
| **PBX IP Address** | `192.168.1.10` | Dedicated Voice Network |
| **PBX HTTPS API Port**| `8089` | Endpoint: `https://192.168.1.10:8089/api` |
| **PBX Web UI Port** | `8443` | Endpoint: `https://192.168.1.10:8443` |
| **SIP Ports** | `5060` (UDP/TCP), `5061` (TLS) | Standard SIP / SIPS |
| **Firmware** | `1.0.33.x` | Core Base Firmware |

---

## 2. Desk Extension & Phone Allocation (Template)

| Ext | User / Station | Switch Port | Phone MAC | Phone IP | Account Type | Status |
|---|---|---|---|---|---|---|
| **1001** | Alice (Executive) | Port 12 | `00-0B-82-11-22-33` | `192.168.1.101` | SIP (WebRTC) | Configured / Active |
| **1002** | Bob (Operations) | Port 13 | `00-0B-82-44-55-66` | `192.168.1.102` | SIP (WebRTC) | Configured / Active |
| **1003** | Charlie (Support) | Port 14 | `00-0B-82-77-88-99` | `192.168.1.103` | SIP (WebRTC) | Configured / Active |
| **1004** | Reception | Port 15 | `00-0B-82-AA-BB-CC` | `192.168.1.104` | SIP (WebRTC) | Configured / Active |

---

## 3. Network Architecture Guidelines

- **Voice VLAN (e.g. VLAN 20)**:
  - 802.1Q Tag: 20
  - 802.1p Priority: 6 (High Priority Voice Traffic)
- **Data Pass-Through (e.g. Office Data VLAN 10)**:
  - Workstation connects to the phone's **PC Port**.
  - Untagged data packets from PC pass through phone transparently.
  - Desk phone tags its own SIP/RTP packets with 802.1Q Voice VLAN.
