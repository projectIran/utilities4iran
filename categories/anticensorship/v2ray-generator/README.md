# v2ray-generator

DPI-resistant V2Ray/Xray configuration generator

## Installation

```bash
cd categories/anticensorship/v2ray-generator
```

## Usage

```python
V2RAY_UUID=11111111-2222-4333-8444-555555555555 \
V2RAY_SERVER_IP=203.0.113.10 \
V2RAY_SNI_DOMAIN=edge.example.org \
python3 src/generator.py
```

## Testing

```bash
./tests/test-generator.sh
```

## Security

See SECURITY.md for security considerations.
