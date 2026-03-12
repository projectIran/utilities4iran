const test = require('node:test');
const assert = require('node:assert/strict');
const { stripMetadata } = require('../src/metadataStripper');

function buildFakeJpegWithExifGps() {
  const soi = Buffer.from([0xff, 0xd8]);
  const exifPayload = Buffer.from('Exif\0\0Make=TestCam;GPSLatitude=35.6892;GPSLongitude=51.3890', 'ascii');
  const app1Length = Buffer.alloc(2);
  app1Length.writeUInt16BE(exifPayload.length + 2, 0);
  const app1Exif = Buffer.concat([Buffer.from([0xff, 0xe1]), app1Length, exifPayload]);
  const sosAndImageData = Buffer.from([0xff, 0xda, 0x00, 0x08, 0x01, 0x01, 0x00, 0x00, 0x3f, 0x00, 0x11, 0x22, 0x33, 0x44, 0xff, 0xd9]);
  return Buffer.concat([soi, app1Exif, sosAndImageData]);
}

test('stripMetadata removes GPS content from APP1 Exif and preserves scan data', () => {
  const input = buildFakeJpegWithExifGps();
  assert.equal(input.includes(Buffer.from('GPS', 'ascii')), true);
  const output = stripMetadata(input);
  assert.equal(output.includes(Buffer.from('GPS', 'ascii')), false);
  assert.equal(output.includes(Buffer.from('Exif', 'ascii')), false);
  assert.equal(output[0], 0xff);
  assert.equal(output[1], 0xd8);
  assert.equal(output.includes(Buffer.from([0x11, 0x22, 0x33, 0x44])), true);
});
