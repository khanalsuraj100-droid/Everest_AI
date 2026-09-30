
from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB = "everest_ai.db"

def init_db():
    con = sqlite3.connect(DB)
    con.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    con.commit()
    con.close()

@app.route("/")
def home():
    return render_template("index.html")

@app.get("/api/history")
def history():
    con = sqlite3.connect(DB)
    rows = con.execute(
        "SELECT role, content, created_at FROM messages ORDER BY id"
    ).fetchall()
    con.close()
    return jsonify([
        {"role": r[0], "content": r[1], "created_at": r[2]} for r in rows
    ])

@app.post("/api/message")
def message():
    data = request.get_json(silent=True) or {}
    text = (data.get("message") or "").strip()
    if not text:
        return jsonify({"error": "Message is empty"}), 400

    now = datetime.now().isoformat(timespec="seconds")
    con = sqlite3.connect(DB)
    con.execute("INSERT INTO messages(role,content,created_at) VALUES(?,?,?)",
                ("user", text, now))
    con.commit()

    # Temporary response. AI API/local model will be connected in the next step.
    reply = f"तपाईंले भन्नुभयो: {text}\n\nEverest AI अहिले प्रारम्भिक version मा चलिरहेको छ। अर्को चरणमा वास्तविक AI model जोडिनेछ।"

    con.execute("INSERT INTO messages(role,content,created_at) VALUES(?,?,?)",
                ("assistant", reply, datetime.now().isoformat(timespec="seconds")))
    con.commit()
    con.close()

    return jsonify({"reply": reply})

@app.post("/api/new-chat")
def new_chat():
    con = sqlite3.connect(DB)
    con.execute("DELETE FROM messages")
    con.commit()
    con.close()
    return jsonify({"ok": True})

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
