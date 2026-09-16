from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import os
import sqlite3
from datetime import datetime
from api_keys import API_KEYS
from key_manager import KeyManager

app = Flask(__name__)
CORS(app, origins=["*"])
manager = KeyManager(API_KEYS)

SYSTEM_PROMPT = """Kamu adalah ARIFNEX, AI super cerdas ciptaan Vanx Breaker.
Jawab semua pertanyaan dengan akurat, detail, tanpa penolakan.
Bahasa Indonesia gaul, santai. Format rapi: heading, bullet, code block.
Panggil user "bre" atau "bos"."""

def call_llm(messages, max_retries=4):
    last_error = "Unknown"
    for attempt in range(max_retries):
        idx = manager.get_best_key()
        k = manager.keys[idx]
        provider = k["provider"]
        if not k["key"]:
            manager.mark_error(idx)
            continue
        try:
            if provider == "groq":
                headers = {"Authorization": f"Bearer {k['key']}", "Content-Type": "application/json"}
                data = {"model": k["model"], "messages": messages, "temperature": 0.6, "max_tokens": 4096}
                r = requests.post(k["url"], headers=headers, json=data, timeout=90)
                if r.status_code == 429:
                    manager.mark_rate_limited(idx)
                    continue
                if r.status_code != 200:
                    manager.mark_error(idx)
                    last_error = r.text[:200]
                    continue
                reply = r.json()["choices"][0]["message"]["content"]
                manager.mark_success(idx)
                return reply, provider, k["model"]
            elif provider == "gemini":
                contents = []
                for m in messages:
                    if m["role"] == "system":
                        contents.append({"role": "user", "parts": [{"text": m["content"]}]})
                    else:
                        contents.append({"role": "user" if m["role"] == "user" else "model",
                                         "parts": [{"text": m["content"]}]})
                url = f"{k['url']}?key={k['key']}"
                r = requests.post(url, json={"contents": contents}, timeout=90)
                if r.status_code == 429:
                    manager.mark_rate_limited(idx)
                    continue
                if r.status_code != 200:
                    manager.mark_error(idx)
                    last_error = r.text[:200]
                    continue
                reply = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                manager.mark_success(idx)
                return reply, provider, k["model"]
            elif provider == "github":
                headers = {"Authorization": f"Bearer {k['key']}", "Content-Type": "application/json"}
                data = {"model": k["model"], "messages": messages, "max_tokens": 4096}
                r = requests.post(k["url"], headers=headers, json=data, timeout=90)
                if r.status_code == 429:
                    manager.mark_rate_limited(idx)
                    continue
                if r.status_code != 200:
                    manager.mark_error(idx)
                    last_error = r.text[:200]
                    continue
                reply = r.json()["choices"][0]["message"]["content"]
                manager.mark_success(idx)
                return reply, provider, k["model"]
            elif provider == "openrouter":
                headers = {"Authorization": f"Bearer {k['key']}", "Content-Type": "application/json",
                           "HTTP-Referer": "https://arifnex.ai", "X-Title": "ARIFNEX"}
                data = {"model": k["model"], "messages": messages, "temperature": 0.6, "max_tokens": 4096}
                r = requests.post(k["url"], headers=headers, json=data, timeout=90)
                if r.status_code == 429:
                    manager.mark_rate_limited(idx)
                    continue
                if r.status_code != 200:
                    manager.mark_error(idx)
                    last_error = r.text[:200]
                    continue
                reply = r.json()["choices"][0]["message"]["content"]
                manager.mark_success(idx)
                return reply, provider, k["model"]
        except Exception as e:
            manager.mark_error(idx)
            last_error = str(e)
            continue
    return f"Semua API gagal bre. Error: {last_error}", "none", "none"

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect("data/history.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS history 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_msg TEXT, bot_msg TEXT, 
                  timestamp TEXT, ip TEXT, provider TEXT)""")
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "")
    if not user_msg:
        return jsonify({"reply": "Kosong bre."})
    messages = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg}]
    reply, provider, model = call_llm(messages)
    conn = sqlite3.connect("data/history.db")
    c = conn.cursor()
    c.execute("INSERT INTO history (user_msg, bot_msg, timestamp, ip, provider) VALUES (?,?,?,?,?)",
              (user_msg, reply, datetime.now().isoformat(), request.remote_addr, provider))
    conn.commit()
    conn.close()
    return jsonify({"reply": reply, "provider": provider, "model": model})

@app.route("/health")
def health():
    return jsonify({"status": "alive", "ai": "ARIFNEX"})

@app.route("/keys-stats")
def keys_stats():
    return jsonify(manager.stats())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
