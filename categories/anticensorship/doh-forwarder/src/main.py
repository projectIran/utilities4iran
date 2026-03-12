#!/usr/bin/env python3

import argparse
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


PROVIDERS = {
    "cloudflare": "https://cloudflare-dns.com/dns-query",
    "google": "https://dns.google/resolve",
    "quad9": "https://dns.quad9.net:5053/dns-query",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Forward DNS lookups to trusted DNS-over-HTTPS providers."
    )
    parser.add_argument("query", help="DNS name to resolve, for example example.org")
    parser.add_argument("--type", default="A", help="DNS record type to request")
    return parser.parse_args()


def get_provider_name():
    provider_name = os.environ.get("DOH_PROVIDER", "").strip().lower()
    if not provider_name:
        print(
            "Error: DOH_PROVIDER must be set to cloudflare, google, or quad9.",
            file=sys.stderr,
        )
        sys.exit(1)

    if provider_name not in PROVIDERS:
        print(
            "Error: Unsupported DOH_PROVIDER. Use cloudflare, google, or quad9.",
            file=sys.stderr,
        )
        sys.exit(1)

    return provider_name


def build_request(provider_name, query_name, record_type):
    params = urlencode({"name": query_name, "type": record_type})
    return Request(
        f"{PROVIDERS[provider_name]}?{params}",
        headers={"accept": "application/dns-json"},
    )


def forward_query(provider_name, query_name, record_type):
    request = build_request(provider_name, query_name, record_type)
    with urlopen(request, timeout=5) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def main():
    try:
        args = parse_args()
        provider_name = get_provider_name()
        response_data = forward_query(provider_name, args.query, args.type)
        json.dump(
            {
                "provider": provider_name,
                "query": args.query,
                "type": args.type,
                "response": response_data,
            },
            sys.stdout,
            indent=2,
        )
        sys.stdout.write("\n")
    except SystemExit:
        raise
    except (HTTPError, URLError, TimeoutError):
        print(
            "Error: DNS-over-HTTPS network request failed.",
            file=sys.stderr,
        )
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: DNS-over-HTTPS provider returned invalid JSON.", file=sys.stderr)
        sys.exit(1)
    except Exception:
        print("Error: Unable to process the DNS query safely.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
