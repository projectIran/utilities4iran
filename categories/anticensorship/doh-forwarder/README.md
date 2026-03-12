# doh-forwarder

Encrypted DNS-over-HTTPS forwarder to prevent local DNS hijacking

## Installation

```bash
cd categories/anticensorship/doh-forwarder
```

## Usage

```python
DOH_PROVIDER=cloudflare python3 src/main.py example.org
```

## Testing

```bash
./tests/test-doh.sh
```

## Security

See SECURITY.md for security considerations.
