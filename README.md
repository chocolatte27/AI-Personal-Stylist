# AI Personal Stylist

A rebuild of your Smart Wardrobe Organizer project — Flask backend, HTML/CSS/JS
frontend, Groq for outfit suggestions, OpenWeatherMap for weather-aware styling.

## Project structure

```
ai-personal-stylist/
├── app.py                  # Flask backend (routes, wardrobe storage, AI + weather)
├── requirements.txt
├── .env.example             # copy to .env / export these yourself
├── wardrobe_data.json       # local "database" — seeded with sample items
├── templates/
│   └── index.html           # AI Stylist / My Closet / Insights tabs
└── static/
    ├── css/style.css        # pink theme matching your report's UI screenshots
    └── js/app.js             # tab switching, wardrobe CRUD, outfit calls
```

## Setup

```bash
cd ai-personal-stylist
pip install -r requirements.txt

export GROQ_API_KEY="your-new-groq-key"
export WEATHER_API_KEY="your-openweathermap-key"   # optional — city weather still works without it via manual entry

$env:GROQ_API_KEY = "your-real-key"
$env:WEATHER_API_KEY = "your-real-key"

python app.py
```

Then open **http://127.0.0.1:5000**.

If `GROQ_API_KEY` isn't set, the AI Stylist tab still works — it just returns
a generic fallback outfit tip instead of a live Groq-generated one, so you can
demo the UI without keys configured.

## What's implemented (mapped to your report's requirements)

- **AI Stylist Module** — occasion + mood pills, style preference text field,
  weather (live city lookup or manual description), Groq-generated outfit text.
- **Wardrobe Management Module** — add / delete items, mark as worn, filter
  by category, seeded with the same sample closet from your screenshots.
- **Weather Integration Module** — `/api/weather` and inline lookup inside
  `/api/outfit`, with a manual-entry fallback per your reliability requirement
  ("even if external services like the weather API fail, the application
  should still work").
- **Insights Dashboard** — most-worn / least-worn / never-worn items,
  category breakdown, optional cost-per-wear (add a price when creating an
  item to see it).
- **Local storage only** — `wardrobe_data.json`, no database server, no
  multi-user accounts, matching the report's stated scope.

## Notes / things to extend later

- `app.secret_key` is now a random value generated per run unless you set
  `FLASK_SECRET_KEY`, so sessions won't survive a server restart — fine for a
  prototype, set a fixed value if you need persistent sessions.
- The Groq model is set to `llama-3.3-70b-versatile` in `app.py` — swap it
  for whichever model you have access to if that one isn't available on your
  account.
