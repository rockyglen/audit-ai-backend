import requests
import os

# This is the official NIST Cybersecurity Framework 2.0 (Public Domain)
# It is dense, complex, and perfect for testing RAG.
PDF_URL = "https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf"
FILENAME = "nist_framework.pdf"


def download_real_pdf():
    print(f"📡 Connecting to NIST Government Server...")
    print(f"🔗 URL: {PDF_URL}")

    response = requests.get(PDF_URL)

    if response.status_code == 200:
        with open(FILENAME, "wb") as f:
            f.write(response.content)
        print(f"\n✅ Success! Downloaded: {FILENAME}")
        print(f"📊 File Size: {len(response.content) / 1024:.2f} KB")
        print("📝 This is a REAL regulatory document with complex structure.")
    else:
        print(f"❌ Failed to download. Status Code: {response.status_code}")


if __name__ == "__main__":
    download_real_pdf()
