const { Octokit } = require('@octokit/rest');
const https = require('https');

// Maximum characters of diff to send to Gemini API to stay within token limits
const MAX_DIFF_LENGTH = 12000;

const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });

async function callGemini(prompt) {
  const payload = JSON.stringify({
    contents: [{ parts: [{ text: prompt }] }],
    generationConfig: {
      temperature: 0.2,
      maxOutputTokens: 2048,
    }
  });

  return new Promise((resolve, reject) => {
    const req = https.request({
      hostname: 'generativelanguage.googleapis.com',
      path: `/v1/models/gemini-2.5-flash:generateContent?key=${process.env.GEMINI_API_KEY}`,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(payload)
      }
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode !== 200) {
          reject(new Error(`Gemini API error: ${res.statusCode} - ${data}`));
          return;
        }
        try {
          const json = JSON.parse(data);
          resolve(json.candidates[0].content.parts[0].text);
        } catch (e) {
          reject(new Error(`Parse error: ${e.message}`));
        }
      });
    });
    
    req.on('error', reject);
    req.write(payload);
    req.end();
  });
}

async function main() {
  if (!process.env.GEMINI_API_KEY) {
    console.warn('⚠️ GEMINI_API_KEY is missing. Mock Mode enabled; skipping AI security audit.');
    return;
  }

  const { PR_NUMBER, REPO_OWNER, REPO_NAME } = process.env;
  
  console.log(`🔍 Analyzing PR #${PR_NUMBER}...`);

  const { data: diff } = await octokit.rest.pulls.get({
    owner: REPO_OWNER,
    repo: REPO_NAME,
    pull_number: PR_NUMBER,
    mediaType: { format: 'diff' }
  });

  const { data: files } = await octokit.rest.pulls.listFiles({
    owner: REPO_OWNER,
    repo: REPO_NAME,
    pull_number: PR_NUMBER,
  });

  const filenames = files.map(f => f.filename);
  const hasTests = filenames.some(f => /test|spec/.test(f));
  const isDocsOnly = filenames.every(f => /\.(md|txt)$/.test(f) || f.startsWith('docs/'));

  if (isDocsOnly) {
    console.log('✓ Docs-only change');
    await postReview('APPROVE', '✅ Documentation update - no security review needed');
    return;
  }

  const prompt = `You are a security auditor for utilities4iran, an activist tooling repository.

Analyze this PR diff for:
1. Obfuscated code (base64, hex, eval, exec)
2. Suspicious network calls
3. Missing test coverage

PR has tests: ${hasTests}

Respond ONLY with JSON:
{
  "verdict": "ACCEPT" or "REJECT",
  "summary": "brief finding",
  "issues": ["issue1", "issue2"],
  "risk": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
}

DIFF:
\`\`\`
${diff.substring(0, MAX_DIFF_LENGTH)}
\`\`\``;

  console.log('🤖 Querying Gemini...');
  const aiResponse = await callGemini(prompt);
  
  const jsonMatch = aiResponse.match(/\{[\s\S]*\}/);
  if (!jsonMatch) throw new Error('No JSON in AI response');
  
  const review = JSON.parse(jsonMatch[0]);

  if (!hasTests && !isDocsOnly) {
    review.issues.push('⚠️ No test files detected');
    review.verdict = 'REJECT';
  }

  const body = `### 🤖 Gatekeeper Review

**Verdict:** ${review.verdict === 'ACCEPT' ? '✅ ACCEPT' : '❌ REJECT'}  
**Risk:** ${review.risk}

${review.summary}

${review.issues.length > 0 ? `**Issues:**\n${review.issues.map(i => `- ${i}`).join('\n')}` : ''}

---
<sub>Powered by Gemini AI (free tier)</sub>`;

  const event = review.verdict === 'ACCEPT' ? 'APPROVE' : 'REQUEST_CHANGES';
  await postReview(event, body);

  if (event === 'REQUEST_CHANGES') {
    console.error('❌ PR REJECTED');
    process.exit(1);
  }

  console.log('✅ PR APPROVED');
}

async function postReview(event, body) {
  await octokit.rest.pulls.createReview({
    owner: process.env.REPO_OWNER,
    repo: process.env.REPO_NAME,
    pull_number: process.env.PR_NUMBER,
    body,
    event
  });
}

main().catch(err => {
  console.error('💥 Error:', err);
  process.exit(1);
});
