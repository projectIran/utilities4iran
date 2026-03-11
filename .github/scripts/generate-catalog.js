const fs = require('fs');
const path = require('path');

function getRepositorySlug() {
  return process.env.GITHUB_REPOSITORY || 'projectIran/utilities4iran';
}

function listDirectories(dirPath) {
  if (!fs.existsSync(dirPath)) {
    return [];
  }

  return fs
    .readdirSync(dirPath, { withFileTypes: true })
    .filter((dirent) => dirent.isDirectory())
    .map((dirent) => dirent.name)
    .sort();
}

function hasMeaningfulFiles(dirPath) {
  if (!fs.existsSync(dirPath)) {
    return false;
  }

  const entries = fs.readdirSync(dirPath, { withFileTypes: true });

  for (const entry of entries) {
    if (entry.name.startsWith('.')) {
      continue;
    }

    const fullPath = path.join(dirPath, entry.name);

    if (entry.isFile()) {
      return true;
    }

    if (entry.isDirectory() && hasMeaningfulFiles(fullPath)) {
      return true;
    }
  }

  return false;
}

function findSourceExtension(modulePath) {
  const srcDir = path.join(modulePath, 'src');

  if (!fs.existsSync(srcDir)) {
    return null;
  }

  const entries = fs.readdirSync(srcDir, { withFileTypes: true });

  for (const entry of entries) {
    if (entry.isFile()) {
      const ext = path.extname(entry.name).toLowerCase();
      if (ext) {
        return ext;
      }
    }
  }

  return null;
}

function extractDescription(content) {
  if (!content) {
    return null;
  }

  const lines = content.split(/\r?\n/);
  let foundTitle = false;

  for (const rawLine of lines) {
    const line = rawLine.trim();

    if (!foundTitle) {
      if (line.startsWith('# ')) {
        foundTitle = true;
      }
      continue;
    }

    if (!line) {
      continue;
    }

    if (line.startsWith('#') || line.startsWith('```') || line.startsWith('- ') || line.startsWith('* ')) {
      continue;
    }

    return line.substring(0, 200);
  }

  return null;
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

async function scanUtilities() {
  const categoriesDir = path.join(__dirname, '../../categories');
  const modules = [];

  if (!fs.existsSync(categoriesDir)) {
    console.warn('⚠️  categories/ directory not found');
    return modules;
  }

  const categories = listDirectories(categoriesDir);

  for (const category of categories) {
    const categoryPath = path.join(categoriesDir, category);
    const moduleNames = listDirectories(categoryPath);

    for (const moduleName of moduleNames) {
      const modulePath = path.join(categoryPath, moduleName);
      const readmePath = path.join(modulePath, 'README.md');
      const readme = fs.existsSync(readmePath) ? fs.readFileSync(readmePath, 'utf8') : '';
      const metadata = parseModule(readme, moduleName, category, modulePath);
      modules.push(metadata);
    }
  }

  return modules;
}

function parseModule(content, name, category, modulePath) {
  const titleMatch = content ? content.match(/^#\s+([^\n]+)/m) : null;
  const title = titleMatch ? titleMatch[1] : name;

  const description = extractDescription(content) || `Module in the ${category} category.`;

  const hasTests = hasMeaningfulFiles(path.join(modulePath, 'tests')) ||
                   hasMeaningfulFiles(path.join(modulePath, 'test'));
  const hasSource = hasMeaningfulFiles(path.join(modulePath, 'src'));
  const hasSecurity = fs.existsSync(path.join(modulePath, 'SECURITY.md'));
  const hasReadme = fs.existsSync(path.join(modulePath, 'README.md'));

  const language = detectLanguage(modulePath);
  const qualityScore = calculateQuality({
    hasTests,
    hasSecurity,
    hasSource,
    hasReadme,
    descLength: description.length,
  });
  const repositorySlug = getRepositorySlug();

  return {
    name,
    category,
    title,
    description,
    language,
    hasSource,
    hasTests,
    hasSecurity,
    qualityScore,
    path: `categories/${category}/${name}`,
    url: `https://github.com/${repositorySlug}/tree/main/categories/${category}/${name}`
  };
}

function detectLanguage(modulePath) {
  if (fs.existsSync(path.join(modulePath, 'package.json'))) return 'JavaScript';
  if (fs.existsSync(path.join(modulePath, 'requirements.txt'))) return 'Python';
  if (fs.existsSync(path.join(modulePath, 'go.mod'))) return 'Go';
  if (fs.existsSync(path.join(modulePath, 'Cargo.toml'))) return 'Rust';

  const ext = findSourceExtension(modulePath);
  if (ext === '.js' || ext === '.mjs' || ext === '.cjs') return 'JavaScript';
  if (ext === '.py') return 'Python';
  if (ext === '.go') return 'Go';
  if (ext === '.rs') return 'Rust';

  return 'Other';
}

function calculateQuality({ hasTests, hasSecurity, hasSource, hasReadme, descLength }) {
  let score = 20;
  if (hasReadme) score += 10;
  if (hasSource) score += 30;
  if (hasTests) score += 25;
  if (hasSecurity) score += 15;
  if (descLength > 50) score += 10;
  return Math.min(score, 100);
}

function generateHTML(modules) {
  // Sanitize module data before embedding in HTML to prevent XSS
  const sanitized = modules.map(m => ({
    ...m,
    name: escapeHtml(m.name),
    title: escapeHtml(m.title),
    description: escapeHtml(m.description),
    language: escapeHtml(m.language),
    path: escapeHtml(m.path),
    // URL is generated internally from the module name, but sanitize as a precaution
    url: escapeHtml(m.url)
  }));
  const sorted = [...sanitized].sort((a, b) => b.qualityScore - a.qualityScore);
  const avgQuality = modules.length > 0
    ? Math.round(modules.reduce((s, m) => s + m.qualityScore, 0) / modules.length)
    : 0;
  
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>utilities4iran - Module Catalog</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: #0d1117;
      color: #c9d1d9;
      line-height: 1.6;
      padding: 2rem;
    }
    .container { max-width: 1400px; margin: 0 auto; }
    header {
      text-align: center;
      padding: 3rem 0;
      border-bottom: 2px solid #30363d;
    }
    h1 { font-size: 3rem; color: #58a6ff; margin-bottom: 1rem; }
    .subtitle { color: #8b949e; font-size: 1.2rem; }
    .stats {
      display: flex;
      justify-content: center;
      gap: 2rem;
      margin-top: 1.5rem;
      font-size: 0.95rem;
    }
    .stat { color: #8b949e; }
    .stat strong { color: #58a6ff; }
    .search-section {
      margin: 2rem 0;
      background: #161b22;
      padding: 1.5rem;
      border-radius: 8px;
      border: 1px solid #30363d;
    }
    #search {
      width: 100%;
      padding: 0.75rem 1rem;
      background: #0d1117;
      border: 1px solid #30363d;
      border-radius: 6px;
      color: #c9d1d9;
      font-size: 1rem;
    }
    #search:focus {
      outline: none;
      border-color: #58a6ff;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
      gap: 1.5rem;
      margin-top: 2rem;
    }
    .card {
      background: #161b22;
      border: 1px solid #30363d;
      border-radius: 8px;
      padding: 1.5rem;
      transition: all 0.2s;
    }
    .card:hover {
      transform: translateY(-3px);
      border-color: #58a6ff;
      box-shadow: 0 8px 24px rgba(88, 166, 255, 0.1);
    }
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: start;
      margin-bottom: 1rem;
    }
    .card-title {
      font-size: 1.3rem;
      color: #58a6ff;
      text-decoration: none;
      font-weight: 600;
    }
    .card-title:hover { text-decoration: underline; }
    .quality {
      padding: 0.25rem 0.75rem;
      border-radius: 12px;
      font-size: 0.85rem;
      font-weight: 600;
    }
    .quality-high { background: #238636; color: #fff; }
    .quality-med { background: #9e6a03; color: #fff; }
    .quality-low { background: #da3633; color: #fff; }
    .badges {
      display: flex;
      gap: 0.5rem;
      flex-wrap: wrap;
      margin-bottom: 1rem;
    }
    .badge {
      padding: 0.25rem 0.75rem;
      border-radius: 12px;
      font-size: 0.8rem;
      font-weight: 500;
      background: #21262d;
      color: #c9d1d9;
    }
    .badge-test { background: #238636; color: #fff; }
    .badge-security { background: #1f6feb; color: #fff; }
    .description {
      color: #8b949e;
      margin-bottom: 1rem;
      font-size: 0.95rem;
      line-height: 1.5;
    }
    .card-footer {
      padding-top: 1rem;
      border-top: 1px solid #21262d;
    }
    .view-btn {
      display: inline-block;
      padding: 0.5rem 1.25rem;
      background: #238636;
      color: #fff;
      text-decoration: none;
      border-radius: 6px;
      font-size: 0.9rem;
      font-weight: 500;
      transition: background 0.2s;
    }
    .view-btn:hover { background: #2ea043; }
    .no-results {
      text-align: center;
      padding: 4rem;
      color: #8b949e;
      display: none;
    }
    footer {
      margin-top: 4rem;
      padding-top: 2rem;
      border-top: 1px solid #30363d;
      text-align: center;
      color: #6e7681;
      font-size: 0.9rem;
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>🇮🇷 utilities4iran</h1>
      <p class="subtitle">Secure, standalone utility modules for developers</p>
      <div class="stats">
        <span class="stat"><strong>${modules.length}</strong> modules</span>
        <span class="stat"><strong>${avgQuality}</strong> avg quality</span>
        <span class="stat"><strong>${modules.filter(m => m.hasTests).length}</strong> with tests</span>
      </div>
    </header>

    <div class="search-section">
      <input type="text" id="search" placeholder="🔍 Search modules by name, description, or language..." />
    </div>

    <div class="grid" id="grid"></div>
    <div class="no-results" id="no-results">
      <h2>No modules found</h2>
      <p>Try adjusting your search</p>
    </div>

    <footer>
      <p>Part of Project Iran • <a href="https://github.com/Utilities4Iran Project" style="color: #58a6ff;">View on GitHub</a></p>
    </footer>
  </div>

  <script>
    const modules = ${JSON.stringify(sorted)};
    
    function escapeHtml(str) {
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    }

    function renderModules(filtered) {
      if (filtered === undefined) filtered = modules;
      const grid = document.getElementById('grid');
      const noResults = document.getElementById('no-results');
      
      if (filtered.length === 0) {
        grid.style.display = 'none';
        noResults.style.display = 'block';
        return;
      }
      
      grid.style.display = 'grid';
      noResults.style.display = 'none';
      
      grid.innerHTML = filtered.map(function(m) {
        const qualityClass = m.qualityScore >= 75 ? 'high' : m.qualityScore >= 50 ? 'med' : 'low';
        const sourceBadge = m.hasSource ? '<span class="badge badge-test">&#9874; Source</span>' : '';
        const testsBadge = m.hasTests ? '<span class="badge badge-test">&#10003; Tests</span>' : '';
        const securityBadge = m.hasSecurity ? '<span class="badge badge-security">&#128274; Security</span>' : '';
        return '<div class="card">' +
          '<div class="card-header">' +
          '<a href="' + escapeHtml(m.url) + '" class="card-title" target="_blank" rel="noopener noreferrer">' + escapeHtml(m.title) + '</a>' +
          '<span class="quality quality-' + qualityClass + '">' + escapeHtml(String(m.qualityScore)) + '</span>' +
          '</div>' +
          '<div class="badges">' +
          '<span class="badge">' + escapeHtml(m.category) + '</span>' +
          '<span class="badge">' + escapeHtml(m.language) + '</span>' +
          sourceBadge +
          testsBadge +
          securityBadge +
          '</div>' +
          '<p class="description">' + escapeHtml(m.description) + '</p>' +
          '<div class="card-footer">' +
          '<a href="' + escapeHtml(m.url) + '" class="view-btn" target="_blank" rel="noopener noreferrer">View Module &#8594;</a>' +
          '</div>' +
          '</div>';
      }).join('');
    }
    
    document.getElementById('search').addEventListener('input', function(e) {
      const q = e.target.value.toLowerCase();
      const filtered = modules.filter(function(m) {
        return m.title.toLowerCase().indexOf(q) !== -1 ||
          m.category.toLowerCase().indexOf(q) !== -1 ||
          m.description.toLowerCase().indexOf(q) !== -1 ||
          m.language.toLowerCase().indexOf(q) !== -1;
      });
      renderModules(filtered);
    });
    
    renderModules();
  </script>
</body>
</html>`;
}

async function main() {
  console.log('🔍 Scanning categories...');
  const modules = await scanUtilities();
  
  console.log(`📦 Found ${modules.length} modules`);
  
  const html = generateHTML(modules);
  const htmlPath = path.join(__dirname, '../../docs/index.html');
  
  fs.mkdirSync(path.dirname(htmlPath), { recursive: true });
  fs.writeFileSync(htmlPath, html);
  
  console.log(`✅ Generated catalog at ${htmlPath}`);
  if (modules.length > 0) {
    console.log(`📊 Avg quality: ${Math.round(modules.reduce((s, m) => s + m.qualityScore, 0) / modules.length)}`);
  }
}

main().catch(console.error);
