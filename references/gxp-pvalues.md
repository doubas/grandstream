# Grandstream GXP1628 Configuration & P-Value Reference

This document explains the Grandstream GXP series (specifically GXP1628) programmatic provisioning API, internal GWT web endpoints, P-values dictionary, and LCD display flags.

---

## 1. Authentication & API Endpoints

The GXP1628 IP Phone runs an embedded web server with a CGI-based API:

### Login Flow
- **Endpoint**: `POST http://<phone_ip>/cgi-bin/dologin`
- **Headers**:
  ```http
  Referer: http://<phone_ip>/webapp.html
  Origin: http://<phone_ip>
  User-Agent: Mozilla/5.0
  Content-Type: application/x-www-form-urlencoded; charset=UTF-8
  ```
- **Payload**: `password=<admin_password>` (Default: `admin`)
- **Response**:
  ```json
  {"response": "success", "body": {"sid": "abcdef1234567890", "type": "0"}}
  ```
- **Session Cookie**:
  Subsequent requests must supply:
  ```http
  Cookie: session-role=admin; session-identity=<sid>
  ```

### Push Configuration (P-Values)
- **Endpoint**: `POST http://<phone_ip>/cgi-bin/api.values.post`
- **Headers**: Include session cookie and form URL-encoded content type.
- **Payload**: Key-value pairs of P-values plus `"sid": "<sid>"`.

### Soft Reboot / Reload
- **Endpoint**: `GET http://<phone_ip>/cgi-bin/api-sys_operation?passcode=admin&request=REBOOT`
- Required after LCD / Account Name changes (`P270`, `P2380`) to reload the phone's hardware LCD display driver.

---

## 2. Essential P-Values Dictionary

| P-Value | Name | Description / Valid Values | Example Setting |
|---|---|---|---|
| **P47** | Primary SIP Server | FQDN or IP of SIP server / PBX | `192.168.1.10` |
| **P35** | SIP User ID | Numeric extension ID | e.g. `1001` |
| **P36** | Authenticate ID | Authentication username (often same as ext) | e.g. `1001` |
| **P34** | Authenticate Password | SIP extension password / secret | PBX-generated secret |
| **P270** | Account Name | Line key name and screen display label | e.g. `User Name` |
| **P3** | Display Name | Caller ID name sent in SIP INVITE | e.g. `User Name` |
| **P2380**| Account Display Mode | Controls what is shown on LCD: `0` = User Name (`P270`), `1` = User ID (`P35`) | `0` (Displays User Name) |
| **P271** | Account Active | Enables Account 1: `0` = No, `1` = Yes | `1` |
| **P51** | Voice VLAN Tag | 802.1Q VLAN ID for voice packets | `20` |
| **P87** | Voice 802.1p Priority | Layer 2 QoS priority (0-7) | `6` |
| **P229** | PC Port VLAN Tag | VLAN tag for downstream PC port (`0` = untagged pass-through) | `0` |
| **P232** | Layer 3 QoS SIP | DiffServ / DSCP for SIP signaling | `26` (AF31) |
| **P233** | Layer 3 QoS Audio | DiffServ / DSCP for RTP audio | `46` (Expedited Forwarding) |

---

## 3. Python Automation Example

```python
import requests

def configure_phone(ip: str, ext: str, secret: str, name: str, pbx_ip: str = "192.168.1.10"):
    headers = {'Referer': f'http://{ip}/webapp.html'}
    # 1. Login
    login = requests.post(f'http://{ip}/cgi-bin/dologin', data={'password': 'admin'}, headers=headers, timeout=5).json()
    sid = login['body']['sid']
    
    # 2. Push P-Values
    headers['Cookie'] = f'session-role=admin; session-identity={sid}'
    payload = {
        'P47': pbx_ip,
        'P35': ext,
        'P36': ext,
        'P34': secret,
        'P270': name,
        'P3': name,
        'P2380': '0',
        'P271': '1',
        'P51': '20',
        'P87': '6',
        'P229': '0',
        'sid': sid
    }
    requests.post(f'http://{ip}/cgi-bin/api.values.post', data=payload, headers=headers, timeout=5)
    
    # 3. Soft Reboot
    requests.get(f'http://{ip}/cgi-bin/api-sys_operation?passcode=admin&request=REBOOT', timeout=5)
```
