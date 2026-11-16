# PDF Vector Compressor (Android & Desktop)

An advanced, high-performance tool designed to compress complex vector PDF files (such as CAD drawings, architectural blueprints, and vector-heavy documents) by detecting and deduplicating recurring vector paths into reusable Form XObjects, backed by `zlib` compression.

Now featuring a sleek **Flet (Python)** cross-platform graphical user interface optimized for **Android** and desktop environments!

---

## 🚀 What's New in Update 4 (Android Release)
* **Flet 1.x Architecture:** Fully migrated to Flet 1.x, ensuring smooth execution and removing legacy bugs.
* **Android Native Integration:** 
  * Custom sleek app icon integration (`assets/icon.png`).
  * Automatic output directory structuring (`/Download/PDF_Compressed/`).
  * Built-in native file picker and file sharing (`ft.Share`) support to instantly share compressed PDFs via WhatsApp, Telegram, etc.
* **Vector Deduplication Engine (`vec_dedup.py`):** Deep parsing of PDF operator streams (`m`, `l`, `c`, `v`, `y`, `re`, painting operators), grouping repeated vector geometries, and compressing streams with maximum `zlib` level 9.

---

## 📂 Project Structure
```text
PDF_new/
├── main.py            # Flet GUI application & Android event handlers
├── vec_dedup.py       # Core PDF vector deduplication & compression engine
├── pyproject.toml     # Project metadata, Flet configurations & Android permissions
└── assets/
    └── icon.png       # Custom application icon