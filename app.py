from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime
import re

from pdf_search import scan_pdfs

app = Flask(__name__)
DB = "everest_ai.db"


# -------------------------------------------------
# DATABASE
# -------------------------------------------------

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


# -------------------------------------------------
# LOAD PDF KNOWLEDGE
# -------------------------------------------------

print("\nLoading Everest AI knowledge...")

PDF_DATA = scan_pdfs()

print("Knowledge loaded:", len(PDF_DATA), "pages")


# -------------------------------------------------
# TEXT SEARCH
# -------------------------------------------------

def normalize_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def search_knowledge(question, max_results=3):

    question = normalize_text(question)

    if not question:
        return []

    # Question बाट महत्वपूर्ण शब्द निकाल्ने
    words = question.split()

    # धेरै सामान्य शब्द हटाउने
    stop_words = {
        "के", "को", "का", "कि", "कसरी", "कहाँ",
        "कहिले", "किन", "हो", "छ", "भयो", "भए",
        "गर्न", "गर्ने", "बारेमा", "मलाई", "यो",
        "त्यो", "एक", "र", "मा", "ले", "लाई",
        "बाट", "का", "को"
    }

    keywords = [
        word for word in words
        if len(word) >= 2 and word not in stop_words
    ]

    if not keywords:
        keywords = words

    results = []

    for page in PDF_DATA:

        page_text = normalize_text(page["text"])

        score = 0

        for keyword in keywords:

            # exact word
            if keyword in page_text:
                score += 1

            # keyword दोहोरिएको छ भने बढी weight
            count = page_text.count(keyword)

            if count > 1:
                score += min(count, 3)

        if score > 0:
            results.append({
                "score": score,
                "file": page["file"],
                "page": page["page"],
                "text": page["text"]
            })

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results[:max_results]


# -------------------------------------------------
# CREATE ANSWER FROM SEARCH RESULT
# -------------------------------------------------

def generate_reply(question):

    results = search_knowledge(question)

    if not results:
        return (
            "माफ गर्नुहोस्, अहिले मेरो उपलब्ध ज्ञानमा "
            "यस प्रश्नसँग सम्बन्धित जानकारी भेटिएन।\n\n"
            "— Everest AI"
        )

    best = results[0]

    text = best["text"]

    # धेरै लामो text नदेखाउने
    if len(text) > 1500:
        text = text[:1500] + "..."

    reply = (
        f"तपाईंको प्रश्नसँग सम्बन्धित जानकारी भेटियो।\n\n"
        f"{text}\n\n"
        f"📖 स्रोत: {best['file']}, "
        f"पृष्ठ {best['page']}\n\n"
        f"— Everest AI"
    )

    return reply


# -------------------------------------------------
# HOME
# -------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# -------------------------------------------------
# HISTORY
# -------------------------------------------------

@app.get("/api/history")
def history():

    con = sqlite3.connect(DB)

    rows = con.execute(
        "SELECT role, content, created_at "
        "FROM messages ORDER BY id"
    ).fetchall()

    con.close()

    return jsonify([
        {
            "role": r[0],
            "content": r[1],
            "created_at": r[2]
        }
        for r in rows
    ])


# -------------------------------------------------
# MESSAGE
# -------------------------------------------------

@app.post("/api/message")
def message():

    data = request.get_json(silent=True) or {}

    text = (data.get("message") or "").strip()

    if not text:
        return jsonify({
            "error": "Message is empty"
        }), 400

    now = datetime.now().isoformat(
        timespec="seconds"
    )

    con = sqlite3.connect(DB)

    # User message save
    con.execute(
        """
        INSERT INTO messages
        (role, content, created_at)
        VALUES (?, ?, ?)
        """,
        ("user", text, now)
    )

    con.commit()

    # PDF knowledge बाट answer
    reply = generate_reply(text)

    # Assistant response save
    con.execute(
        """
        INSERT INTO messages
        (role, content, created_at)
        VALUES (?, ?, ?)
        """,
        (
            "assistant",
            reply,
            datetime.now().isoformat(
                timespec="seconds"
            )
        )
    )

    con.commit()
    con.close()

    return jsonify({
        "reply": reply
    })


# -------------------------------------------------
# NEW CHAT
# -------------------------------------------------

@app.post("/api/new-chat")
def new_chat():

    con = sqlite3.connect(DB)

    con.execute(
        "DELETE FROM messages"
    )

    con.commit()
    con.close()

    return jsonify({
        "ok": True
    })


# -------------------------------------------------
# START
# -------------------------------------------------

init_db()


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
