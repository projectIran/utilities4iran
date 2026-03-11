const test = require('node:test');
const assert = require('node:assert/strict');
const net = require('node:net');
const { checkBridge } = require('../src/index');

test('checkBridge detects open port and measures latency', async () => {
  const server = net.createServer((s) => s.end());
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const { port } = server.address();

  const result = await checkBridge('127.0.0.1', port, 1000);
  assert.equal(result.status, 'open');
  assert.ok(result.latency >= 0);

  server.close();
});

test('checkBridge detects blocked/closed port', async () => {
  // Use a port that is guaranteed to be closed
  const result = await checkBridge('127.0.0.1', 9999, 100);
  assert.equal(result.status, 'blocked');
});
