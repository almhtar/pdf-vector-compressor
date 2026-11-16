# Vector PDF Optimizer & Compression Engine 🚀

An advanced local automation pipeline designed to compress massive, vector-based PDF documents down to their absolute physical minimum without sacrificing vector path sharpness, font bolding layers, interactive hyperlinks (`/URI`), QR codes, or digital seals.

---

## 🛠️ Tech Stack & Requirements
* **Operating System:** Windows (PowerShell 5.1+)
* **Core Tools:** 
  * `qpdf` (Structure decryption, object streams generation, and Flate recompression)
  * `MuPDF (mutool)` (Vector stream extraction and deep cleaning)
  * `Python` (Custom vector glyph deduplication and Form XObject engineering)

---

## 📂 Project Structure
```text
PDF_work/
│
├── compress_pdf.bat        # Quick launcher & Drag-and-Drop batch automation script
├── compress_engine.ps1     # Core PowerShell orchestration pipeline
└── vec_dedup.py            # Python engine for vector deduplication & Form XObjects