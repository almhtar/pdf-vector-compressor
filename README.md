# PDF Vector & Form XObject Compression Engine 🚀

An advanced local automation script designed to compress massive, vector-based PDF documents (such as multi-page bank statements) to the absolute physical minimum without sacrificing vector path sharpness, font bolding layers, hyperlinks (`/URI`), QR codes, or digital seals.

---

## 🛠️ Tech Stack & Requirements
* **Operating System:** Windows (PowerShell 5.1+)
* **Tools Used:** 
  * `qpdf` (Structure decryption, object streams generation, and Flate recompression)
  * `MuPDF (mutool)` (Vector stream extraction and deep cleaning)
  * `Python` (Custom vector glyph deduplication and Form XObject engineering)

---

## 📂 Project Structure
```text
PDF_work/
│
├── compress_pdf.bat        # Quick launcher & Drag-and-Drop batch script
├── compress_engine.ps1     # Core PowerShell orchestration pipeline
└── vec_dedup.py            # Python engine for vector deduplication & Form XObjects