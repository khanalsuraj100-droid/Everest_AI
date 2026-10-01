import os
import re
import npttf2utf
from pypdf import PdfReader

KNOWLEDGE_DIR = "knowledge"

# Preeti → Unicode converter
MAP_FILE = os.path.join(
    os.path.dirname(npttf2utf.__file__),
    "map.json"
)

mapper = npttf2utf.FontMapper(MAP_FILE)


def clean_text(text):
    if not text:
        return ""

    # Preeti → Unicode
    try:
        text = mapper.map_to_unicode(text, from_font="Preeti")
    except Exception as e:
        print("Unicode conversion error:", e)

    # धेरै whitespace हटाउने
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def scan_pdfs():
    results = []

    for root, dirs, files in os.walk(KNOWLEDGE_DIR):
        for filename in files:

            if not filename.lower().endswith(".pdf"):
                continue

            path = os.path.join(root, filename)

            print(f"\nReading: {path}")

            try:
                reader = PdfReader(path)

                print(f"Pages: {len(reader.pages)}")

                for page_number, page in enumerate(reader.pages, start=1):

                    text = page.extract_text() or ""
                    text = clean_text(text)

                    if text:
                        results.append({
                            "file": filename,
                            "path": path,
                            "page": page_number,
                            "text": text
                        })

                print("Done.")

            except Exception as e:
                print(f"ERROR: {e}")

    return results


if __name__ == "__main__":

    data = scan_pdfs()

    print("\n-----------------------------")
    print("PDF SEARCH INDEX")
    print("-----------------------------")

    print("Total searchable pages:", len(data))

    if data:
        print("\nFirst page sample:")
        print(data[0]["text"][:1000])
