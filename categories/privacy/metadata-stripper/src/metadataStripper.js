function isJpeg(buffer) {
  return buffer.length >= 2 && buffer[0] === 0xff && buffer[1] === 0xd8;
}
function isStandaloneMarker(marker) {
  return marker === 0x01 || marker === 0xd8 || marker === 0xd9 || (marker >= 0xd0 && marker <= 0xd7);
}
function isExifApp1(marker, payload) {
  return marker === 0xe1 && payload.length >= 4 && payload.subarray(0, 4).toString('ascii') === 'Exif';
}
function stripMetadata(buffer) {
  if (!Buffer.isBuffer(buffer)) throw new TypeError('buffer must be a Buffer');
  if (!isJpeg(buffer)) return Buffer.from(buffer);
  const chunks = [buffer.subarray(0, 2)];
  let offset = 2;
  while (offset < buffer.length) {
    if (buffer[offset] !== 0xff) { chunks.push(buffer.subarray(offset)); break; }
    let markerOffset = offset;
    while (markerOffset < buffer.length && buffer[markerOffset] === 0xff) markerOffset += 1;
    if (markerOffset >= buffer.length) break;
    const marker = buffer[markerOffset];
    const markerStart = markerOffset - 1;
    if (marker === 0xda) { chunks.push(buffer.subarray(markerStart)); break; }
    if (isStandaloneMarker(marker)) {
      chunks.push(buffer.subarray(markerStart, markerOffset + 1));
      offset = markerOffset + 1;
      continue;
    }
    if (markerOffset + 2 >= buffer.length) { chunks.push(buffer.subarray(markerStart)); break; }
    const segmentLength = buffer.readUInt16BE(markerOffset + 1);
    const segmentEnd = markerOffset + 1 + segmentLength;
    if (segmentLength < 2 || segmentEnd > buffer.length) { chunks.push(buffer.subarray(markerStart)); break; }
    const payload = buffer.subarray(markerOffset + 3, segmentEnd);
    if (!isExifApp1(marker, payload)) chunks.push(buffer.subarray(markerStart, segmentEnd));
    offset = segmentEnd;
  }
  return Buffer.concat(chunks);
}
module.exports = { stripMetadata };
