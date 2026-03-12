function extractHashtags(text) {
  const value = String(text || '');
  const matches = value.match(/#([A-Za-z0-9_]+)/g) || [];
  return matches.map((tag) => tag.slice(1).toLowerCase());
}

function normalizeHashtags(hashtags) {
  if (!Array.isArray(hashtags)) {
    return [];
  }

  const normalized = hashtags
    .map((tag) => String(tag || '').trim().replace(/^#/, '').toLowerCase())
    .filter((tag) => /^[a-z0-9_]+$/.test(tag));

  return Array.from(new Set(normalized));
}

function splitIntoThread(text, maxLength = 260) {
  const value = String(text || '').trim();
  if (!value) {
    return [];
  }

  if (!Number.isInteger(maxLength) || maxLength < 50 || maxLength > 280) {
    throw new Error('maxLength must be an integer between 50 and 280.');
  }

  const words = value.split(/\s+/);
  const chunks = [];
  let current = '';

  for (const word of words) {
    const candidate = current ? `${current} ${word}` : word;
    if (candidate.length <= maxLength) {
      current = candidate;
      continue;
    }

    if (!current) {
      chunks.push(word.slice(0, maxLength));
      current = word.slice(maxLength);
      continue;
    }

    chunks.push(current);
    current = word;
  }

  if (current) {
    chunks.push(current);
  }

  return chunks;
}

function buildPostingSchedule(startTime, count, intervalMinutes = 30) {
  const start = new Date(startTime);
  if (Number.isNaN(start.getTime())) {
    throw new Error('startTime must be a valid date/time value.');
  }

  if (!Number.isInteger(count) || count < 1) {
    throw new Error('count must be a positive integer.');
  }

  if (!Number.isInteger(intervalMinutes) || intervalMinutes < 1) {
    throw new Error('intervalMinutes must be a positive integer.');
  }

  const schedule = [];
  for (let i = 0; i < count; i += 1) {
    const publishAt = new Date(start.getTime() + i * intervalMinutes * 60 * 1000);
    schedule.push(publishAt.toISOString());
  }

  return schedule;
}

function createPostPlan(options) {
  const text = String(options && options.text ? options.text : '').trim();
  if (!text) {
    throw new Error('text is required.');
  }

  const thread = splitIntoThread(text, options && options.maxLength ? options.maxLength : 260);
  const tags = normalizeHashtags([
    ...(options && options.hashtags ? options.hashtags : []),
    ...extractHashtags(text),
  ]);
  const schedule = buildPostingSchedule(
    options && options.startTime ? options.startTime : new Date().toISOString(),
    thread.length,
    options && options.intervalMinutes ? options.intervalMinutes : 30
  );

  const posts = thread.map((body, index) => ({
    body,
    publishAt: schedule[index],
  }));

  return {
    hashtags: tags,
    posts,
  };
}

module.exports = {
  extractHashtags,
  normalizeHashtags,
  splitIntoThread,
  buildPostingSchedule,
  createPostPlan,
};
