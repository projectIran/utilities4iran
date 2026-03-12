const net = require('node:net');

function checkBridge(host, port, timeout = 3000) {
  return new Promise((resolve) => {
    const start = process.hrtime.bigint();
    const socket = net.createConnection({ host, port });
    let settled = false;

    const timer = setTimeout(() => {
      if (settled) return;
      settled = true;
      socket.destroy();
      resolve({ status: 'blocked', error: 'timeout' });
    }, timeout);

    socket.once('connect', () => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      const latency = Number((process.hrtime.bigint() - start) / 1000000n);
      socket.destroy();
      resolve({ status: 'open', latency });
    });

    socket.once('error', (err) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      socket.destroy();
      resolve({ status: 'blocked', error: err.message });
    });
  });
}

module.exports = { checkBridge };
