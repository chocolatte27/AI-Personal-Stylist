"""
AI Personal Stylist — Flask backend
------------------------------------
Reconstructed from the project report (AI Personal Stylist / Smart Wardrobe
Organizer) and the app.py screenshot supplied by the user.

Setup:
  1. pip install -r requirements.txt
  2. Set your own keys as environment variables (see .env.example) —
     NEVER hardcode real API keys in this file, especially not in a
     screenshot or a public repo.
       export GROQ_API_KEY="your-groq-key"
       export WEATHER_API_KEY="your-openweathermap-key"   # optional
  3. python app.py
  4. Open http://127.0.0.1:5000
"""

import json
import os
import uuid
from pathlib import Path

import requests
from flask import Flask, jsonify, request, render_template

try:
    from groq import Groq
except ImportError:  # groq package not installed yet — app still runs, AI calls fall back
    Groq = None

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24).hex())

# Read keys from the environment instead of hardcoding them in source.
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY", "")

GROQ_MODEL = "openai/gpt-oss-120b"

client = Groq(api_key=GROQ_API_KEY) if (GROQ_API_KEY and Groq) else None

DATA_FILE = Path(__file__).parent / "wardrobe_data.json"

DEFAULT_CATEGORIES = ["Tops", "Jeans", "Ethnic", "Gym Wear", "Dresses"]


# ---------------------------------------------------------------------------
# Local "database" — a simple JSON file (per the report's local-storage /
# single-user scope, no cloud, no multi-user accounts).
# ---------------------------------------------------------------------------

def load_wardrobe():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_wardrobe(items):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)


def seed_if_empty():
    if not DATA_FILE.exists():
        seed = [
            {"id": str(uuid.uuid4()), "name": "White tee", "category": "Tops", "worn": 2, "price": None},
            {"id": str(uuid.uuid4()), "name": "Blue jeans", "category": "Jeans", "worn": 3, "price": None},
            {"id": str(uuid.uuid4()), "name": "Floral kurta", "category": "Ethnic", "worn": 1, "price": None},
            {"id": str(uuid.uuid4()), "name": "Track pants", "category": "Gym Wear", "worn": 5, "price": None},
            {"id": str(uuid.uuid4()), "name": "Black hoodie", "category": "Tops", "worn": 0, "price": None},
            {"id": str(uuid.uuid4()), "name": "Salwar set", "category": "Ethnic", "worn": 2, "price": None},
            {"id": str(uuid.uuid4()), "name": "Sports wear", "category": "Gym Wear", "worn": 4, "price": None},
            {"id": str(uuid.uuid4()), "name": "Maxi dress", "category": "Dresses", "worn": 0, "price": None},
            {"id": str(uuid.uuid4()), "name": "Denim jacket", "category": "Tops", "worn": 1, "price": None},
            {"id": str(uuid.uuid4()), "name": "Leggings", "category": "Gym Wear", "worn": 8, "price": None},
        ]
        save_wardrobe(seed)


seed_if_empty()


# ---------------------------------------------------------------------------
# Weather module (OpenWeatherMap) — optional; the app should still work
# via the "describe it manually" fallback if this fails or no key is set.
# ---------------------------------------------------------------------------

def get_weather(city):
    if not WEATHER_API_KEY or not city:
        return None
    try:
        url = (
            "http://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={WEATHER_API_KEY}&units=metric"
        )
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return None
        data = r.json()
        return {
            "city": data.get("name", city),
            "temp": round(data["main"]["temp"]),
            "description": data["weather"][0]["description"],
        }
    except requests.RequestException:
        return None


# ---------------------------------------------------------------------------
# AI Stylist module (Groq)
# ---------------------------------------------------------------------------

def build_outfit_prompt(occasion, mood, preferences, weather_text, wardrobe_items):
    closet_lines = "\n".join(
        f"- {i['name']} ({i['category']}, worn {i['worn']}x)" for i in wardrobe_items
    ) or "(closet is empty — suggest general items)"

    return f"""You are a friendly, concise personal stylist. Suggest ONE outfit.

Occasion: {occasion or "not specified"}
Mood: {mood or "not specified"}
Style preferences: {preferences or "none given"}
Weather: {weather_text or "unknown"}

Here is the user's wardrobe (prefer items from here, favor underused items
over frequently worn ones when they fit):
{closet_lines}

Respond in 2-3 short sentences: name the specific pieces to wear together,
then one quick styling tip. Keep it warm and practical, no headers, no
markdown, no emoji spam (one is fine)."""


def generate_outfit(occasion, mood, preferences, weather_text, wardrobe_items):
    if client is None:
        # Fallback so the app still demos without a key configured.
        return (
            "Set GROQ_API_KEY to get live AI styling. For now: try your "
            "most versatile top with a comfortable bottom that suits the "
            "weather, and add one accent piece for the occasion."
        )
    prompt = build_outfit_prompt(occasion, mood, preferences, weather_text, wardrobe_items)
    completion = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
        max_tokens=600,
        reasoning_effort="low",
    )
    content = completion.choices[0].message.content
    return content.strip() if content else (
    "The stylist drew a blank — try again."
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html", categories=DEFAULT_CATEGORIES)


@app.route("/api/wardrobe", methods=["GET"])
def api_get_wardrobe():
    return jsonify(load_wardrobe())


@app.route("/api/wardrobe", methods=["POST"])
def api_add_item():
    payload = request.get_json(force=True) or {}
    name = (payload.get("name") or "").strip()
    category = payload.get("category") or "Tops"
    price = payload.get("price")

    if not name:
        return jsonify({"error": "Item name is required."}), 400

    items = load_wardrobe()
    new_item = {
        "id": str(uuid.uuid4()),
        "name": name,
        "category": category,
        "worn": 0,
        "price": price,
    }
    items.append(new_item)
    save_wardrobe(items)
    return jsonify(new_item), 201


@app.route("/api/wardrobe/<item_id>", methods=["DELETE"])
def api_delete_item(item_id):
    items = load_wardrobe()
    remaining = [i for i in items if i["id"] != item_id]
    if len(remaining) == len(items):
        return jsonify({"error": "Item not found."}), 404
    save_wardrobe(remaining)
    return jsonify({"deleted": item_id})


@app.route("/api/wardrobe/<item_id>/wear", methods=["POST"])
def api_mark_worn(item_id):
    items = load_wardrobe()
    for i in items:
        if i["id"] == item_id:
            i["worn"] += 1
            save_wardrobe(items)
            return jsonify(i)
    return jsonify({"error": "Item not found."}), 404


@app.route("/api/weather")
def api_weather():
    city = request.args.get("city", "")
    weather = get_weather(city)
    if weather is None:
        return jsonify({"available": False})
    return jsonify({"available": True, **weather})


@app.route("/api/outfit", methods=["POST"])
def api_outfit():
    payload = request.get_json(force=True) or {}
    occasion = payload.get("occasion", "")
    mood = payload.get("mood", "")
    preferences = payload.get("preferences", "")
    city = payload.get("city", "")
    manual_weather = payload.get("manual_weather", "")

    weather_text = manual_weather
    weather_info = None
    if not manual_weather and city:
        weather_info = get_weather(city)
        if weather_info:
            weather_text = f"{weather_info['temp']}°C, {weather_info['description']} in {weather_info['city']}"

    wardrobe_items = load_wardrobe()
    outfit_text = generate_outfit(occasion, mood, preferences, weather_text, wardrobe_items)

    return jsonify({
        "outfit": outfit_text,
        "weather": weather_info,
        "weather_text": weather_text,
    })


@app.route("/api/insights")
def api_insights():
    items = load_wardrobe()
    if not items:
        return jsonify({
            "most_worn": [], "least_worn": [], "never_worn": [],
            "total_items": 0, "total_wears": 0, "cost_per_wear": [],
            "category_breakdown": {},
        })

    by_worn = sorted(items, key=lambda i: i["worn"], reverse=True)
    never_worn = [i for i in items if i["worn"] == 0]
    total_wears = sum(i["worn"] for i in items)

    category_breakdown = {}
    for i in items:
        category_breakdown[i["category"]] = category_breakdown.get(i["category"], 0) + 1

    cost_per_wear = []
    for i in items:
        if i.get("price"):
            wears = max(i["worn"], 1)
            cost_per_wear.append({
                "name": i["name"],
                "cost_per_wear": round(i["price"] / wears, 2),
            })
    cost_per_wear.sort(key=lambda x: x["cost_per_wear"], reverse=True)

    return jsonify({
        "most_worn": by_worn[:3],
        "least_worn": [i for i in by_worn[::-1] if i["worn"] > 0][:3],
        "never_worn": never_worn,
        "total_items": len(items),
        "total_wears": total_wears,
        "cost_per_wear": cost_per_wear[:5],
        "category_breakdown": category_breakdown,
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
