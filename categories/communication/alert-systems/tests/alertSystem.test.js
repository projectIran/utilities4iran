const test = require('node:test');
const assert = require('node:assert/strict');

const {
  validateAlert,
  prepareAlert,
  deduplicateAlerts,
} = require('../src/alertSystem');

test('validateAlert rejects invalid payloads', () => {
  const { ok, errors } = validateAlert({
    message: '',
    channel: 'unknown',
    severity: 'panic',
    createdAt: 'bad-date',
  });

  assert.equal(ok, false);
  assert.equal(errors.length >= 3, true);
});

test('prepareAlert normalizes alert payload', () => {
  const prepared = prepareAlert(
    {
      message: '  Power outage in district 4  ',
      channel: 'Telegram',
      severity: 'HIGH',
    },
    () => new Date('2026-03-11T10:00:00.000Z')
  );

  assert.equal(prepared.message, 'Power outage in district 4');
  assert.equal(prepared.channel, 'telegram');
  assert.equal(prepared.severity, 'high');
  assert.equal(prepared.createdAt, '2026-03-11T10:00:00.000Z');
  assert.equal(typeof prepared.id, 'string');
});

test('deduplicateAlerts removes duplicates inside the time window', () => {
  const alerts = [
    { message: 'Road blocked', channel: 'sms', createdAt: '2026-03-11T09:00:00.000Z' },
    { message: 'Road blocked', channel: 'sms', createdAt: '2026-03-11T09:03:00.000Z' },
    { message: 'Road blocked', channel: 'sms', createdAt: '2026-03-11T09:12:00.000Z' },
  ];

  const unique = deduplicateAlerts(alerts, 5 * 60 * 1000);
  assert.equal(unique.length, 2);
});
