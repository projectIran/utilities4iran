const test = require('node:test');
const assert = require('node:assert/strict');

const {
  extractHashtags,
  splitIntoThread,
  buildPostingSchedule,
  createPostPlan,
} = require('../src/postPlanner');

test('extractHashtags normalizes hashtag tokens', () => {
  const tags = extractHashtags('Update #Iran #Connectivity #IRAN');
  assert.deepEqual(tags, ['iran', 'connectivity', 'iran']);
});

test('splitIntoThread creates multiple chunks when needed', () => {
  const text = 'One two three four five six seven eight nine ten eleven twelve';
  const chunks = splitIntoThread(text, 50);
  assert.equal(chunks.length > 1, true);
});

test('buildPostingSchedule returns deterministic intervals', () => {
  const schedule = buildPostingSchedule('2026-03-11T12:00:00.000Z', 3, 15);
  assert.deepEqual(schedule, [
    '2026-03-11T12:00:00.000Z',
    '2026-03-11T12:15:00.000Z',
    '2026-03-11T12:30:00.000Z',
  ]);
});

test('createPostPlan creates posts and merges hashtags', () => {
  const plan = createPostPlan({
    text: 'Connectivity alert in city center #Urgent',
    hashtags: ['Iran', '#urgent'],
    startTime: '2026-03-11T12:00:00.000Z',
    intervalMinutes: 20,
    maxLength: 280,
  });

  assert.equal(plan.posts.length, 1);
  assert.deepEqual(plan.hashtags, ['iran', 'urgent']);
  assert.equal(plan.posts[0].publishAt, '2026-03-11T12:00:00.000Z');
});
