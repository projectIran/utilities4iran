# metadata-stripper
Removes EXIF/GPS metadata from JPEGs.
## Features
- Pure Node.js implementation.
- Removes APP1 segments.
## Usage
\`\`\`javascript
const { stripMetadata } = require('./src/metadataStripper');
\`\`\`
## Testing
\`\`\`bash
node --test tests/metadataStripper.test.js
\`\`\`
