# metadata-stripper

Removes EXIF and GPS metadata from JPEG image buffers without relying on native binaries or external services.

## Features
- Strip all APP1 Exif segments (includes GPS coordinates, camera model, timestamps)
- Preserve compressed scan data intact — output is a valid JPEG
- Pure Node.js, no native addons or third-party dependencies

## Usage
\`\`\`javascript
const { stripMetadata } = require('./src/metadataStripper');
const fs = require('node:fs');

const input = fs.readFileSync('photo.jpg');
const clean = stripMetadata(input);

fs.writeFileSync('photo-clean.jpg', clean);
\`\`\`

## Testing
\`\`\`bash
node --test tests/metadataStripper.test.js
\`\`\`
