# Iran Policy Radar — Social Media Action Dashboard

A web-based dashboard for the Iranian diaspora advocacy community to track, engage with, and contact US decision-makers on Iran policy.

## Features

- **200 Decision-Makers**: Tracks 100 anti-war Democrats and 100 pro-war Republicans
- **Quick Access**: Direct links to X (Twitter) profiles and email addresses
- **Smart Filtering**: Filter by priority, category (Congress, Senate, Executive, Think Tanks, Media, etc.)
- **Search**: Instantly search by name, role, or social handle
- **Random Pick**: Get a random person to engage with — great for distributed advocacy
- **AI Email Generator**: Generate personalized emails with customizable topics and tones
  - Works with OpenAI API for unique AI-generated emails
  - Falls back to template-based generation without an API key

## Quick Start

### Option 1: Static (No Server)

Simply open `index.html` in your browser. Everything works except AI email generation (which falls back to templates client-side).

### Option 2: With Server (Full Features)

```bash
# Install dependencies
pip install -r requirements.txt

# Configure (optional: add OpenAI key for AI emails)
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run the server
python server.py
```

Open http://localhost:8000 in your browser.

## Architecture

```
social-media-radar/
├── index.html          # Main dashboard UI
├── styles.css          # Dark theme styling
├── app.js              # Frontend logic (vanilla JS)
├── server.py           # FastAPI backend (AI email generation)
├── data/
│   ├── democrats.json  # Anti-war decision-makers
│   └── republicans.json # Pro-war decision-makers
├── requirements.txt    # Python dependencies
├── .env.example        # Environment template
└── README.md           # This file
```

## Data Structure

Each person entry contains:

| Field      | Description                              |
|------------|------------------------------------------|
| `id`       | Unique identifier                        |
| `name`     | Full name                                |
| `role`     | Position/title                           |
| `x_handle` | X (Twitter) handle                      |
| `email`    | Contact email                            |
| `category` | congress, senate, executive, think_tank, organization, media, activist, academic |
| `priority` | high, medium, low                        |

## Email Topics

- **Oppose War**: Advocate against military action
- **Diplomacy**: Support diplomatic engagement
- **Sanctions**: Address humanitarian impact of sanctions
- **Human Rights**: Support Iranian civil society
- **Peace**: De-escalation and conflict prevention
- **Custom**: Write your own topic

## Contributing

1. To add or update decision-maker data, edit the JSON files in `data/`
2. Follow the existing data structure
3. Mark priority based on influence level and relevance

## Security

- No personal data is stored
- API keys are kept in `.env` (never committed)
- All social media links open in new tabs
- Email generation is stateless
