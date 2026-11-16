#!/bin/bash
INPUT="$1"
if [ -z "$INPUT" ]; then
    INPUT="input.PDF"
fi

if [ ! -f "$INPUT" ]; then
    echo "Error: Input file '$INPUT' not found!"
    exit 1
fi

BASENAME=$(basename "$INPUT" .PDF)
BASENAME=$(basename "$BASENAME" .pdf)
OUTPUT="${BASENAME}_MaxCompressed.pdf"

echo "[*] Decrypting PDF..."
qpdf --decrypt "$INPUT" temp_dec.pdf 2>/dev/null || cp "$INPUT" temp_dec.pdf

echo "[*] Cleaning vector streams with mutool..."
mutool clean -d -gggg temp_dec.pdf uncomp_ultra.pdf

echo "[*] Running Vector Deduplication Engine..."
python3 vec_dedup.py

echo "[*] Finalizing ultra clean stream with mutool..."
mutool clean -gggg -c -z -e 100 -f -Z ultra_raw.pdf ultra_clean.pdf 2>/dev/null

echo "[*] Recompressing with qpdf..."
qpdf --object-streams=generate --recompress-flate --compression-level=9 ultra_clean.pdf "$OUTPUT"

# Cleanup temporary files
rm -f temp_dec.pdf uncomp_ultra.pdf ultra_raw.pdf ultra_clean.pdf

echo "[+] Done! Compressed file saved as: $OUTPUT"