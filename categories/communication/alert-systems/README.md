# alert-systems

Utilities for validating, normalizing, and deduplicating alert messages before delivery.

## Features

- Validate alert payloads with clear error messages
- Normalize channel and severity values
- Deduplicate repeated alerts within a configurable time window

## Usage

```javascript
const {
  validateAlert,
  prepareAlert,
  deduplicateAlerts,
} = require('./src/alertSystem');

const payload = {
  message: 'Internet disruption in region A',
  channel: 'telegram',
  severity: 'high',
};

const result = validateAlert(payload);
if (!result.ok) {
  console.error(result.errors);
}

const alert = prepareAlert(payload);
const unique = deduplicateAlerts([alert]);
console.log(unique.length);
```

## Testing

```bash
node --test tests/alertSystem.test.js
```
