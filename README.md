# Vector PDF Optimizer & Compression Engine (Android & Desktop) 🚀

An advanced local automation pipeline and cross-platform graphical application designed to compress massive, vector-based PDF documents down to their absolute physical minimum without sacrificing vector path sharpness, font bolding layers, interactive hyperlinks (`/URI`), QR codes, or digital seals.

Now featuring a sleek **Flet (Python)** cross-platform graphical user interface optimized for **Android** and desktop environments alongside the original Windows/Linux CLI automation pipeline!

---

## 🚀 What's New in Update 4 (Android Release)
* **Flet 1.x Architecture:** Fully migrated to Flet 1.x (`ft.run`, `ft.Button`, and service-based `ft.FilePicker`), ensuring smooth execution on Android without legacy crashes.
* **Android Native Integration:**
  * Custom sleek app icon integration (`assets/icon.png`).
  * Automatic output directory structuring (`/storage/emulated/0/Download/PDF_Compressed/`).
  * Built-in native file picker and file sharing (`ft.Share`) support to instantly share compressed PDFs via WhatsApp, Telegram, or email.
* **Enhanced Vector Deduplication Engine (`vec_dedup.py`):** Deep parsing of PDF operator streams (`m`, `l`, `c`, `v`, `y`, `re`, painting operators), automatic `zlib` (`FlateDecode`) decompression/recompression at level 9, and grouping repeated vector geometries into reusable Form XObjects.

---

## 🛠️ Tech Stack & Requirements

### 1. Android & Cross-Platform App (Flet GUI)
* **Python:** 3.10+
* **Framework:** `flet >= 1.1.2`
* **Target Platform:** Android (`arm64-v8a`) & Desktop

### 2. Windows / Linux CLI Pipeline (Legacy & Batch Automation)
* **Operating System:** Windows (PowerShell 5.1+) or Linux/macOS (`bash`)
* **Core Tools:**
  * `qpdf` (Structure decryption, object streams generation, and Flate recompression)
  * `MuPDF (mutool)` (Vector stream extraction and deep cleaning)
  * `Python` (Custom vector glyph deduplication and Form XObject engineering)

---

## 📂 Project Structure
```text
pdf-vector-compressor/
│
├── main.py                 # Flet GUI application & Android event handlers (Picker, Share, Storage)
├── vec_dedup.py            # Core Python engine for vector deduplication, zlib & Form XObjects
├── pyproject.toml          # Project metadata, Flet configurations & Android permissions
├── assets/
│   └── icon.png            # Custom application icon
├── compress_pdf.bat        # Windows quick launcher & Drag-and-Drop batch automation script
├── compress_engine.ps1     # Windows PowerShell orchestration pipeline
└── compress.sh             # Linux/macOS shell automation script
```

---

## 📱 Building & Running the Android APK
To build the standalone Android application package from source, ensure the Android SDK is configured and run:

```powershell
flet build apk --cleanup-app
```

The resulting `.apk` will be generated inside `build/apk/`, ready to be installed on your Android device. Compressed files are automatically saved to `/Download/PDF_Compressed/`.

---

## 💻 Usage (Desktop / CLI)
* **Windows Drag & Drop:** Drag any vector PDF onto `compress_pdf.bat` to run the full `mutool` + `vec_dedup.py` + `qpdf` pipeline.
* **Direct Python API:**
```python
import vec_dedup

templates_count = vec_dedup.compress_pdf("input.pdf", "output_compressed.pdf")
print(f"Compressed successfully using {templates_count} vector templates!")
```