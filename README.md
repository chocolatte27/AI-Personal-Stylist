# AI Personal Stylist

A Flask + HTML/CSS/JS project —
AI-generated outfit suggestions via Groq, weather-aware styling via
OpenWeatherMap, and a local wardrobe manager with a usage-insights dashboard.

## Project structure

```
ai-personal-stylist/
├── app.py                   # Flask backend — routes, wardrobe storage, AI + weather calls
├── requirements.txt         # Python dependencies
├── .env.example              # Template showing which env vars the app needs — NOT real keys
├── .gitignore                 # Keeps .env, wardrobe_data.json, __pycache__ out of git
├── wardrobe_data.json        # Local "database" (JSON file) — seeded with sample items
├── templates/
│   └── index.html            # AI Stylist / My Closet / Insights tabs
└── static/
    ├── css/style.css         # Pink theme matching the original report's UI
    └── js/app.js              # Tab switching, wardrobe CRUD, outfit requests
```

## Setup (Windows / PowerShell)

```powershell
cd ai-personal-stylist
pip install -r requirements.txt
```

Set your API keys for the current terminal session (see **API keys** below
for where to get these):

```powershell
$env:GROQ_API_KEY = "your-groq-key"
$env:WEATHER_API_KEY = "your-openweathermap-key"   # optional
```

Then run the app:

```powershell
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

> **Note:** `$env:` variables only last for the current PowerShell window.
> Close it, and you'll need to set them again next time before running
> `python app.py`. The app reads keys with `os.environ.get(...)` — it does
> **not** currently load a `.env` file automatically.

### Setup (macOS / Linux)

```bash
cd ai-personal-stylist
pip install -r requirements.txt
export GROQ_API_KEY="your-groq-key"
export WEATHER_API_KEY="your-openweathermap-key"
python app.py
```

## API keys

| Variable | Required? | Where to get it |
|---|---|---|
| `GROQ_API_KEY` | For live AI outfit suggestions | console.groq.com → API Keys |
| `WEATHER_API_KEY` | Optional — city lookup won't work without it | openweathermap.org/api (free tier) |

Without `GROQ_API_KEY` set, the AI Stylist tab still works but returns a
generic fallback tip instead of a live suggestion — useful for demoing the
UI without keys configured.

Without `WEATHER_API_KEY`, the city weather lookup returns nothing, but the
**"describe it manually"** field still works as a fallback (e.g. "hot and
humid") — this matches the reliability requirement in the original report.

**Never commit real keys.** `.env.example` is a template only — it should
always contain placeholder text, never an actual key. If you ever paste a
real key into a file, a chat, or a screenshot, treat that key as compromised
and regenerate it from the provider's dashboard.

## What's implemented 

- **AI Stylist Module** — occasion + mood pills, style preference text field,
  weather (live city lookup or manual description), Groq-generated outfit
  text using `openai/gpt-oss-120b`.
- **Wardrobe Management Module** — add / delete items, mark as worn, filter
  by category, seeded with a sample closet (white tee, blue jeans, etc.).
- **Weather Integration Module** — `/api/weather` endpoint plus an inline
  lookup inside `/api/outfit`, with a manual-entry fallback if the weather
  API is unavailable or no key is set.
- **Insights Dashboard** — most-worn / least-worn / never-worn items,
  category breakdown, optional cost-per-wear (add a price when creating an
  item to see it calculated).
- **Local storage only** — `wardrobe_data.json`, no database server, no
  multi-user accounts, matching the report's stated scope.

## Pushing to GitHub

This repo includes a `.gitignore` that excludes `.env` and
`wardrobe_data.json` automatically, so a normal `git add .` won't stage
your secrets or personal test data:

```powershell
git init
git add .
git status          # confirm .env and wardrobe_data.json are NOT listed
git commit -m "Initial commit: AI Personal Stylist"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

If you ever see GitHub's **push protection** block a push because it found a
secret in a commit, don't try to push around it — regenerate that key and
either amend the commit or reset your local history before committing again
cleanly.

## Known limitations / ideas for later

- `app.secret_key` is a random value generated fresh each time the server
  starts (unless `FLASK_SECRET_KEY` is set), so sessions won't persist
  across restarts — fine for a prototype.
- No `.env` file loading yet — keys must be set via `$env:` / `export` each
  session. Can be added with `python-dotenv` if you'd rather set keys once
  in a file.
- If `openai/gpt-oss-120b` ever gets deprecated on Groq's end, check
  console.groq.com/docs/models for its replacement and update `GROQ_MODEL`
  in `app.py`.
