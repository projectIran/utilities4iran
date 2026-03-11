# x-automation

Utility functions for preparing X (Twitter) post plans in a safer and more structured way.

## Features

- Extract and normalize hashtags
- Split long text into thread-sized chunks
- Generate deterministic posting schedules
- Build a complete post plan from one input object

## Usage

```javascript
const { createPostPlan } = require('./src/postPlanner');

const plan = createPostPlan({
  text: 'Service update: connectivity disruptions expected this evening #Iran',
  hashtags: ['Updates'],
  startTime: '2026-03-11T19:00:00.000Z',
  intervalMinutes: 20,
});

console.log(plan);
```

## Testing

```bash
node --test tests/postPlanner.test.js
```
