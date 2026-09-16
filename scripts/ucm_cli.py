#!/usr/bin/env python3
"""
Grandstream UCM6304A PBX & GXP Phone CLI Helper
Interacts with Grandstream HTTPS API (firmware 1.0.33.x) and provisions GXP16xx IP phones.
"""

import os
import sys
import json
import hashlib
import argparse
from pathlib import Path
import urllib3
import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def find_env_file() -> Path:
    current = Path.cwd()
    for p in [current, *current.parents]:
        env_path = p / ".env"
        if env_path.is_file():
            return env_path
    return current / ".env"

def load_env():
    env_file = find_env_file()
    if not env_file.is_file():
        return
    try:
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                if k not in os.environ:
                    os.environ[k] = v
    except Exception as e:
        print(f"[!] Warning: Could not parse .env: {e}", file=sys.stderr)

class GrandstreamClient:
    def __init__(self):
        load_env()
        self.ip = os.getenv("UCM_IP", "127.0.0.1")
        self.port = int(os.getenv("UCM_PORT", "8089"))
        self.username = os.getenv("UCM_USERNAME", "admin")
        self.password = os.getenv("UCM_PASSWORD")
        self.api_url = os.getenv("UCM_URL") or f"https://{self.ip}:{self.port}/api"
        self.cookie = None

        if not self.password:
            print("[!] Error: UCM_PASSWORD not set in environment or .env", file=sys.stderr)
            sys.exit(1)

    def authenticate(self) -> str:
        if self.cookie:
            return self.cookie

        # 1. Challenge
        res_ch = requests.post(
            self.api_url,
            json={"request": {"action": "challenge", "user": self.username, "version": "1.0"}},
            headers={"Content-Type": "application/json;charset=UTF-8"},
            verify=False,
            timeout=10
        ).json()

        if res_ch.get("status") != 0:
            print(f"[!] Challenge failed: {res_ch}", file=sys.stderr)
            sys.exit(1)

        challenge = res_ch.get("response", {}).get("challenge")
        token = hashlib.md5((challenge + self.password).encode("utf-8")).hexdigest()

        # 2. Login
        res_login = requests.post(
            self.api_url,
            json={"request": {"action": "login", "user": self.username, "token": token}},
            headers={"Content-Type": "application/json;charset=UTF-8"},
            verify=False,
            timeout=10
        ).json()

        if res_login.get("status") != 0:
            print(f"[!] Login failed: {res_login}", file=sys.stderr)
            sys.exit(1)

        self.cookie = res_login.get("response", {}).get("cookie")
        return self.cookie

    def request(self, action: str, extra_params: dict = None) -> dict:
        cookie = self.authenticate()
        payload = {"action": action, "cookie": cookie}
        if extra_params:
            payload.update(extra_params)

        resp = requests.post(
            self.api_url,
            json={"request": payload},
            headers={"Content-Type": "application/json;charset=UTF-8"},
            verify=False,
            timeout=15
        )
        try:
            return resp.json()
        except Exception:
            return {"status": -1, "error_msg": resp.text}

    def logout(self):
        if self.cookie:
            try:
                requests.post(
                    self.api_url,
                    json={"request": {"action": "logout", "cookie": self.cookie}},
                    verify=False,
                    timeout=5
                )
            except Exception:
                pass
            self.cookie = None

def cmd_status(client: GrandstreamClient, args):
    gen = client.request("getSystemGeneralStatus")
    sys_st = client.request("getSystemStatus")
    
    if getattr(args, "json", False):
        print(json.dumps({"general": gen, "system": sys_st}, indent=2))
        return

    print("=== GRANDSTREAM UCM6304A SYSTEM STATUS ===")
    g = gen.get("response", {}) if gen.get("status") == 0 else {}
    s = sys_st.get("response", {}) if sys_st.get("status") == 0 else {}

    print(f"Model:           {g.get('product-model', 'UCM6304A')}")
    print(f"Part Number:     {s.get('part-number', '')}")
    print(f"Serial Number:   {s.get('serial-number', '')}")
    print(f"MAC Address:     {s.get('mac', '')}")
    print(f"Firmware:        Core: {g.get('core-version', '')} | Base: {g.get('prog-version', '')}")
    print(f"GS Wave:         {g.get('gswave-version', '')}")
    print(f"Uptime:          {s.get('up-time', '')}")
    print(f"System Time:     {s.get('system-time', '')}")
    client.logout()

def cmd_extensions(client: GrandstreamClient, args):
    res = client.request("listAccount")
    if args.json:
        print(json.dumps(res, indent=2))
        client.logout()
        return

    accounts = res.get("response", {}).get("account", [])
    print(f"{'Extension':<10} | {'Name':<22} | {'Type':<16} | {'Status'}")
    print("-" * 65)
    for a in accounts:
        print(f"{a.get('extension', ''):<10} | {a.get('fullname', ''):<22} | {a.get('account_type', ''):<16} | {a.get('status', '')}")
    print(f"\nTotal: {len(accounts)} extensions configured.")
    client.logout()

def cmd_extension(client: GrandstreamClient, args):
    res = client.request("getSIPAccount", {"extension": args.ext})
    if args.json:
        print(json.dumps(res, indent=2))
        client.logout()
        return

    ext_data = res.get("response", {}).get("extension", {})
    if not ext_data:
        print(f"[!] Extension {args.ext} not found or error: {res}")
    else:
        print(f"=== EXTENSION {args.ext} DETAILS ===")
        print(f"Extension:       {args.ext}")
        print(f"Authenticate ID: {ext_data.get('authid', '')}")
        print(f"SIP Secret:      {ext_data.get('secret', '')}")
        print(f"Display Name:    {ext_data.get('fullname', '')}")
        print(f"Out of Service:  {ext_data.get('out_of_service', '')}")
    client.logout()

def cmd_trunks(client: GrandstreamClient, args):
    analog = client.request("listAnalogTrunk")
    voip = client.request("listVoIPTrunk")
    if args.json:
        print(json.dumps({"analog": analog, "voip": voip}, indent=2))
        client.logout()
        return

    print("=== TRUNKS ===")
    a_trunks = analog.get("response", {}).get("trunk", [])
    print(f"Analog FXO Trunks ({len(a_trunks)}):")
    for t in a_trunks:
        print(f"  - Index: {t.get('trunk_index')} | Name: {t.get('trunk_name')} | Status: {t.get('status')}")

    v_trunks = voip.get("response", {}).get("voiptrunk", [])
    print(f"VoIP / SIP Trunks ({len(v_trunks)}):")
    for t in v_trunks:
        print(f"  - Index: {t.get('trunk_index')} | Name: {t.get('trunk_name')} | Host: {t.get('host_name')}")
    client.logout()

def cmd_routes(client: GrandstreamClient, args):
    inbound = client.request("listInboundRoute")
    outbound = client.request("listOutboundRoute")
    if args.json:
        print(json.dumps({"inbound": inbound, "outbound": outbound}, indent=2))
        client.logout()
        return

    in_routes = inbound.get("response", {}).get("inbound_routes", [])
    print(f"Inbound Routes ({len(in_routes)}):")
    for r in in_routes:
        print(f"  - Route: {r.get('inbound_route_id')} | Pattern: {r.get('pattern')} | Destination: {r.get('destination_type')}")

    out_routes = outbound.get("response", {}).get("outbound_routes", [])
    print(f"Outbound Routes ({len(out_routes)}):")
    for r in out_routes:
        print(f"  - Route: {r.get('outbound_route_id')} | Pattern: {r.get('pattern')} | Trunk: {r.get('trunk_name')}")
    client.logout()

def cmd_request(client: GrandstreamClient, args):
    extra = {}
    if args.params:
        try:
            extra = json.loads(args.params)
        except Exception as e:
            print(f"[!] Invalid JSON params: {e}", file=sys.stderr)
            sys.exit(1)
    res = client.request(args.action, extra)
    print(json.dumps(res, indent=2))
    client.logout()

def cmd_provision_phone(client: GrandstreamClient, args):
    phone_ip = args.ip
    ext = args.ext
    name = args.name
    secret = args.secret
    admin_pw = args.admin_password or os.getenv("GXP_ADMIN_PASSWORD", "admin")

    # If secret or name missing, query UCM automatically!
    if not secret or not name:
        print(f"[*] Querying UCM PBX for extension {ext} details...")
        res = client.request("getSIPAccount", {"extension": ext})
        ext_data = res.get("response", {}).get("extension", {})
        if not ext_data:
            print(f"[!] Could not retrieve extension {ext} from UCM: {res}", file=sys.stderr)
            sys.exit(1)
        if not secret:
            secret = ext_data.get("secret")
            print(f"[+] Retrieved SIP Secret from UCM for ext {ext}")
        if not name:
            name = ext_data.get("fullname", f"Ext {ext}")
            print(f"[+] Retrieved Account Name from UCM: {name}")

    client.logout()

    print(f"[*] Provisioning GXP16xx Phone at {phone_ip} for {name} (Ext {ext})...")
    headers = {
        'Referer': f'http://{phone_ip}/webapp.html',
        'Origin': f'http://{phone_ip}',
        'User-Agent': 'Mozilla/5.0',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }

    # Step 1: Login
    try:
        r_login = requests.post(
            f'http://{phone_ip}/cgi-bin/dologin',
            data={'password': admin_pw},
            headers=headers,
            timeout=6
        ).json()
    except Exception as e:
        print(f"[!] Failed to connect to phone at {phone_ip}: {e}", file=sys.stderr)
        sys.exit(1)

    sid = r_login.get("body", {}).get("sid")
    if not sid:
        print(f"[!] Phone login rejected on {phone_ip}: {r_login}", file=sys.stderr)
        sys.exit(1)
    print(f"[+] Authenticated to phone successfully (SID: {sid})")

    # Step 2: Post P-Values
    headers['Cookie'] = f'session-role=admin; session-identity={sid}'
    payload = {
        'P47': client.ip,            # SIP Server (UCM IP)
        'P35': ext,                  # SIP User ID
        'P36': ext,                  # Authenticate ID
        'P34': secret,               # Authenticate Password
        'P270': name,                # Account Name (Line Key / Screen label)
        'P3': name,                  # Display Name / Caller ID
        'P2380': '0',                # Account Display Mode: 0 = User Name (P270), 1 = User ID
        'P271': '1',                 # Account 1 Active (1=Yes)
        'P51': '20',                 # Layer 2 QoS 802.1Q Voice VLAN Tag (20)
        'P87': '6',                  # Layer 2 QoS 802.1p Priority (6)
        'P229': '0',                 # PC Port VLAN Tag (0=Pass-through)
        'sid': sid
    }

    try:
        r_post = requests.post(
            f'http://{phone_ip}/cgi-bin/api.values.post',
            data=payload,
            headers=headers,
            timeout=6
        ).json()
        print(f"[+] P-values posted successfully: {r_post}")
    except Exception as e:
        print(f"[!] Error posting P-values to {phone_ip}: {e}", file=sys.stderr)
        sys.exit(1)

    # Step 3: Optional Soft Reboot
    if args.reboot:
        try:
            r_reboot = requests.get(
                f'http://{phone_ip}/cgi-bin/api-sys_operation?passcode={admin_pw}&request=REBOOT',
                timeout=6
            ).json()
            print(f"[+] Soft reboot triggered to refresh LCD: {r_reboot}")
        except Exception as e:
            print(f"[!] Warning: Soft reboot request failed: {e}")

    print(f"[+] Done! Extension {ext} ({name}) is provisioned on {phone_ip}.")

def main():
    parser = argparse.ArgumentParser(description="Grandstream UCM PBX & GXP Phone CLI")
    parser.add_argument("--json", action="store_true", help="Output in raw JSON")
    subparsers = parser.add_subparsers(dest="command", help="Command")

    subparsers.add_parser("status", help="Query system hardware & uptime status")
    subparsers.add_parser("extensions", help="List all extensions and users")
    
    p_ext = subparsers.add_parser("extension", help="Get specific extension details and SIP secret")
    p_ext.add_argument("ext", help="Numeric extension (e.g. 102)")

    subparsers.add_parser("trunks", help="List analog and VoIP trunks")
    subparsers.add_parser("routes", help="List inbound and outbound routes")

    p_req = subparsers.add_parser("request", help="Execute an arbitrary Grandstream HTTPS action")
    p_req.add_argument("action", help="Action name from catalog (e.g. listQueue)")
    p_req.add_argument("params", nargs="?", default=None, help="JSON parameters")

    p_prov = subparsers.add_parser("provision-phone", help="Provision GXP16xx IP Phone")
    p_prov.add_argument("--ip", required=True, help="Phone IP address")
    p_prov.add_argument("--ext", required=True, help="Extension number")
    p_prov.add_argument("--name", help="Display name (auto-queried from UCM if omitted)")
    p_prov.add_argument("--secret", help="SIP secret (auto-queried from UCM if omitted)")
    p_prov.add_argument("--admin-password", help="Phone web admin password (defaults to GXP_ADMIN_PASSWORD or 'admin')")
    p_prov.add_argument("--reboot", action="store_true", help="Trigger phone soft reboot to reload LCD labels")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    client = GrandstreamClient()
    commands = {
        "status": cmd_status,
        "extensions": cmd_extensions,
        "extension": cmd_extension,
        "trunks": cmd_trunks,
        "routes": cmd_routes,
        "request": cmd_request,
        "provision-phone": cmd_provision_phone
    }
    commands[args.command](client, args)

if __name__ == "__main__":
    main()
