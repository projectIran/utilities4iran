const { randomUUID } = require('node:crypto');

const ALLOWED_CHANNELS = new Set(['sms', 'email', 'telegram', 'signal', 'webhook']);
const ALLOWED_SEVERITIES = new Set(['low', 'medium', 'high', 'critical']);

function normalizeChannel(channel) {
  return String(channel || '').trim().toLowerCase();
}

function normalizeSeverity(severity) {
  const normalized = String(severity || '').trim().toLowerCase();
  return normalized || 'medium';
}

function validateAlert(input) {
  const errors = [];

  if (!input || typeof input !== 'object' || Array.isArray(input)) {
    return { ok: false, errors: ['Alert must be an object payload.'] };
  }

  if (typeof input.message !== 'string' || !input.message.trim()) {
    errors.push('message is required and must be a non-empty string.');
  }

  if (typeof input.message === 'string' && input.message.trim().length > 500) {
    errors.push('message must be 500 characters or fewer.');
  }

  const channel = normalizeChannel(input.channel);
  if (!ALLOWED_CHANNELS.has(channel)) {
    errors.push(`channel must be one of: ${Array.from(ALLOWED_CHANNELS).join(', ')}.`);
  }

  const severity = normalizeSeverity(input.severity);
  if (!ALLOWED_SEVERITIES.has(severity)) {
    errors.push(`severity must be one of: ${Array.from(ALLOWED_SEVERITIES).join(', ')}.`);
  }

  if (input.createdAt !== undefined) {
    const parsed = new Date(input.createdAt);
    if (Number.isNaN(parsed.getTime())) {
      errors.push('createdAt must be a valid date/time value.');
    }
  }

  return { ok: errors.length === 0, errors };
}

function prepareAlert(input, now = () => new Date()) {
  const validation = validateAlert(input);
  if (!validation.ok) {
    throw new Error(validation.errors.join(' '));
  }

  const createdAt = input.createdAt ? new Date(input.createdAt) : now();

  return {
    id: input.id || randomUUID(),
    message: input.message.trim(),
    channel: normalizeChannel(input.channel),
    severity: normalizeSeverity(input.severity),
    createdAt: createdAt.toISOString(),
    metadata: input.metadata && typeof input.metadata === 'object' && !Array.isArray(input.metadata)
      ? input.metadata
      : {},
  };
}

function deduplicateAlerts(alerts, windowMs = 5 * 60 * 1000) {
  if (!Array.isArray(alerts)) {
    throw new Error('alerts must be an array.');
  }

  const sorted = [...alerts].sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));
  const lastSeenBySignature = new Map();
  const unique = [];

  for (const alert of sorted) {
    const signature = `${String(alert.channel)}|${String(alert.message).trim().toLowerCase()}`;
    const timestamp = new Date(alert.createdAt).getTime();

    if (Number.isNaN(timestamp)) {
      continue;
    }

    const lastSeen = lastSeenBySignature.get(signature);
    if (lastSeen === undefined || timestamp - lastSeen > windowMs) {
      unique.push(alert);
      lastSeenBySignature.set(signature, timestamp);
    }
  }

  return unique;
}

module.exports = {
  ALLOWED_CHANNELS,
  ALLOWED_SEVERITIES,
  validateAlert,
  prepareAlert,
  deduplicateAlerts,
};
