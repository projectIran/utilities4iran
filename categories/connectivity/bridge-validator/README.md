# bridge-validator
TCP health checks for censorship-circumvention bridges.
## Features
- Latency measurement in ms.
- Configurable timeouts.
## Usage
\`\`\`javascript
const { checkBridge } = require('./src/index');
const result = await checkBridge('1.2.3.4', 443);
\`\`\`
