
# Everest AI — Starter

## Linux Mint मा चलाउने

1. Terminal खोल्नुहोस्।
2. यो folder भित्र जानुहोस्:
   `cd ~/everest_ai`  (यदि home मा राख्नुभएको छ भने)
3. Virtual environment बनाउनुहोस्:
   `python3 -m venv venv`
4. Activate:
   `source venv/bin/activate`
5. Flask install:
   `pip install -r requirements.txt`
6. Run:
   `python3 app.py`
7. Browser मा खोल्नुहोस्:
   `http://127.0.0.1:5000`

यो पहिलो version हो। अहिले message र chat history SQLite मा save हुन्छ।
अर्को चरणमा वास्तविक AI model/API जोड्न सकिन्छ।
