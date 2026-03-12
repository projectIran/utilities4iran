#!/usr/bin/env python3

import json
import os
import sys


def load_required_env():
    try:
        uuid = os.environ["V2RAY_UUID"].strip()
        server_ip = os.environ["V2RAY_SERVER_IP"].strip()
        sni_domain = os.environ["V2RAY_SNI_DOMAIN"].strip()
    except KeyError as exc:
        print(f"Error: Missing required environment variable: {exc.args[0]}", file=sys.stderr)
        sys.exit(1)

    if not uuid or not server_ip or not sni_domain:
        print(
            "Error: V2RAY_UUID, V2RAY_SERVER_IP, and V2RAY_SNI_DOMAIN must be set and non-empty.",
            file=sys.stderr,
        )
        sys.exit(1)

    return uuid, server_ip, sni_domain


def build_config(uuid, server_ip, sni_domain):
    return {
        "log": {"loglevel": "warning"},
        "inbounds": [
            {
                "tag": "socks-in",
                "port": 10808,
                "listen": "127.0.0.1",
                "protocol": "socks",
                "settings": {"auth": "noauth", "udp": True},
                "sniffing": {
                    "enabled": True,
                    "destOverride": ["http", "tls"],
                },
            }
        ],
        "outbounds": [
            {
                "tag": "proxy",
                "protocol": "vless",
                "settings": {
                    "vnext": [
                        {
                            "address": server_ip,
                            "port": 443,
                            "users": [
                                {
                                    "id": uuid,
                                    "encryption": "none",
                                }
                            ],
                        }
                    ]
                },
                "streamSettings": {
                    "network": "ws",
                    "security": "tls",
                    "tlsSettings": {
                        "serverName": sni_domain,
                        "allowInsecure": False,
                    },
                    "wsSettings": {
                        "path": "/ws",
                        "headers": {"Host": sni_domain},
                    },
                },
            },
            {"tag": "direct", "protocol": "freedom"},
            {"tag": "blocked", "protocol": "blackhole"},
        ],
        "routing": {
            "domainStrategy": "AsIs",
            "rules": [
                {
                    "type": "field",
                    "ip": ["geoip:private"],
                    "outboundTag": "direct",
                }
            ],
        },
    }


def main():
    try:
        uuid, server_ip, sni_domain = load_required_env()
        json.dump(build_config(uuid, server_ip, sni_domain), sys.stdout, indent=2)
        sys.stdout.write("\n")
    except SystemExit:
        raise
    except Exception as exc:
        print(f"Error: Unable to generate V2Ray configuration: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()