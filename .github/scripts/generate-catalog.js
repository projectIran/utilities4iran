const fs = require('fs');
const path = require('path');

function scanUtilities() {
    const utilitiesDir = path.join(__dirname, '../../categories');
    const modules = [];
    if (!fs.existsSync(utilitiesDir)) return modules;

    const categories = fs.readdirSync(utilitiesDir, { withFileTypes: true })
        .filter(d => d.isDirectory())
        .map(d => d.name);

    for (const cat of categories) {
        const catPath = path.join(utilitiesDir, cat);
        const dirs = fs.readdirSync(catPath, { withFileTypes: true })
            .filter(d => d.isDirectory())
            .map(d => d.name);

        for (const dir of dirs) {
            const modulePath = path.join(catPath, dir);
            const readmePath = path.join(modulePath, 'README.md');
            if (fs.existsSync(readmePath)) {
                const content = fs.readFileSync(readmePath, 'utf8');
                modules.push(parseModule(content, dir, modulePath));
            }
        }
    }
    return modules;
}

function parseModule(content, name, modulePath) {
    const hasTests = fs.existsSync(path.join(modulePath, 'tests')) || fs.existsSync(path.join(modulePath, 'test'));
    const hasSecurity = fs.existsSync(path.join(modulePath, 'SECURITY.md'));
    const description = content.split('\n').find(l => l.length > 10 && !l.startsWith('#')) || 'No description';
    
    return {
        name,
        title: (content.match(/^#\s+(.+)$/m) || [null, name])[1],
        description: description.substring(0, 150),
        hasTests,
        hasSecurity,
        isBridge: name === "v2ray-generator" || name === "bridge-me-bot",
        qualityScore: (hasTests ? 50 : 0) + (hasSecurity ? 50 : 0),
        url: `https://github.com/joojoo47/utilities4iran/tree/main/categories/${path.basename(path.dirname(modulePath))}/${name}`
    };
}

const modules = scanUtilities();
const html = `<!DOCTYPE html>
<html>
<head>
  <title>Tactical Utility Registry</title>
  <style>
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.7; }
    }
    
    body {
      font-family: sans-serif;
      background: #1a1a1a;
      color: #eee;
      padding: 2rem;
      margin: 0;
    }
    
    #status-banner {
      display: none;
      background: #ff4444;
      color: white;
      padding: 1rem;
      text-align: center;
      font-weight: bold;
      margin-bottom: 2rem;
      border-radius: 8px;
      animation: pulse 2s infinite;
    }
    
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 1rem;
    }
    
    .card {
      background: #2a2a2a;
      padding: 1.5rem;
      border-radius: 8px;
      border: 1px solid #444;
    }
    
    .bridge {
      border-color: #ff4444;
      box-shadow: 0 0 10px rgba(255, 68, 68, 0.2);
    }
    
    button {
      background: #ff4444;
      color: white;
      border: none;
      padding: 0.5rem 1rem;
      border-radius: 4px;
      cursor: pointer;
      margin-top: 1rem;
    }
    
    button:hover {
      background: #cc3333;
    }
  </style>
</head>
<body>
  <div id="status-banner"></div>
  <h1>Tactical Utility Registry</h1>
  <div class="grid">
    ${modules.map(m => `
    <div class="card ${m.isBridge ? 'bridge' : ''}">
      <h3>${m.title}</h3>
      <p>${m.description}...</p>
      ${m.isBridge ? `<button onclick="alert('Bridge Request Initiated: Use Signal Bot @bridge_me_bot')">🚨 REQUEST ACCESS</button>` : `<a href="${m.url}" style="color:#44aaee">View Module</a>`}
    </div>`).join('')}
  </div>
  
  <script>
    async function checkStatus() {
      try {
        const response = await fetch('status.json');
        const data = await response.json();
        const banner = document.getElementById('status-banner');
        if (data.alert) {
          banner.style.display = 'block';
          banner.innerHTML = '🚨 CRITICAL: NETWORK DISRUPTION DETECTED. USE EMERGENCY BRIDGES.';
          banner.className = 'status-alert';
        }
      } catch (e) {
        /* Fail silently */
      }
    }
    window.onload = checkStatus;
  </script>
</body>
</html>`;

fs.writeFileSync(path.join(__dirname, '../../docs/index.html'), html);
console.log('✅ Catalog Rebuilt Successfully.');
