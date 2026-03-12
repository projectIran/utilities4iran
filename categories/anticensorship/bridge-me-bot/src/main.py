import json
import os
import subprocess
import sys
import uuid
from urllib.parse import quote

ERROR_MESSAGE = "[ERROR] Unable to generate bridge at this time"


def _extract_vless(output_text):
    data = output_text.strip()
    if data.startswith("vless://"):
        return data

    payload = json.loads(data)
    outbound = payload["outbounds"][0]
    if outbound.get("protocol") != "vless":
        return None

    server = outbound["settings"]["vnext"][0]
    user = server["users"][0]
    stream = outbound["streamSettings"]

    if stream.get("network") != "ws" or stream.get("security") != "tls":
        return None

    address = str(server["address"]).strip()
    port = int(server["port"])
    user_id = str(user["id"]).strip()
    host = str(stream["wsSettings"]["headers"]["Host"]).strip()
    path = str(stream["wsSettings"]["path"]).strip() or "/"
    sni = str(stream["tlsSettings"]["serverName"]).strip()
    encryption = str(user.get("encryption", "none")).strip() or "none"

    if not address or not user_id or not host or not sni:
        return None

    query = (
        f"encryption={quote(encryption, safe='')}&"
        f"security=tls&"
        f"type=ws&"
        f"host={quote(host, safe='')}&"
        f"path={quote(path, safe='')}&"
        f"sni={quote(sni, safe='')}"
    )
    return f"vless://{quote(user_id, safe='')}@{address}:{port}?{query}#bridge-me-bot"


def generate_bridge():
    env = os.environ.copy()
    env.setdefault("V2RAY_UUID", str(uuid.uuid4()))
    env.setdefault("V2RAY_SERVER_IP", "1.1.1.1")
    env.setdefault("V2RAY_SNI_DOMAIN", "www.microsoft.com")

    override = env.get("V2RAY_GENERATOR_PATH", "").strip()
    if override:
        gen_path = override
    else:
        base_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        )
        gen_path = os.path.join(base_dir, "categories/anticensorship/v2ray-generator/src/generator.py")

    python_bin = env.get("PYTHON_BIN", sys.executable)

    try:
        result = subprocess.run(
            [python_bin, gen_path],
            env=env,
            capture_output=True,
            text=True,
            check=True,
        )
        vless = _extract_vless(result.stdout)
        if not vless:
            print(ERROR_MESSAGE, file=sys.stderr)
            sys.exit(1)
        print(vless)
    except Exception:
        print(ERROR_MESSAGE, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if "--cli" in sys.argv:
        generate_bridge()
