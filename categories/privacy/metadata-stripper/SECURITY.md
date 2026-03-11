# Security Policy

## What This Module Does
- Parses JPEG markers and removes APP1 Exif segments, which may contain GPS coordinates, device identifiers, and timestamps.

## What This Module Does Not Do
- **Visual Anonymity:** It does not anonymize faces or visual content. 
- **Format Support:** It does not handle PNG, TIFF, or HEIF.
- **XMP Data:** It does not strip XMP metadata embedded outside of APP1 Exif blocks.

## Reporting
Do not disclose vulnerabilities publicly. Use the repository security contact process.
