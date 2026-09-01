#!/bin/bash
# PDF Extractor Build Script für Mac/Linux

echo "======================================"
echo "PDF Extractor - Build Script"
echo "======================================"
echo ""

# Prüfe ob PyInstaller installiert ist
if ! command -v pyinstaller &> /dev/null; then
    echo "[FEHLER] PyInstaller nicht installiert!"
    echo "Bitte ausführen: pip install pyinstaller"
    exit 1
fi

echo "[1/3] Räume alte Build auf..."
rm -rf build dist *.spec 2>/dev/null

echo "[2/3] Baue Executable..."
if [ -f "icon.icns" ]; then
    pyinstaller --onefile --windowed --icon=icon.icns --name="PDFExtractor" pdf_extractor_app.py
else
    echo "[HINWEIS] icon.icns nicht gefunden - wird ohne Icon gebaut"
    pyinstaller --onefile --windowed --name="PDFExtractor" pdf_extractor_app.py
fi

echo "[3/3] Aufräumen..."
rm -rf build *.spec

if [ -f "dist/PDFExtractor" ] || [ -d "dist/PDFExtractor.app" ]; then
    echo ""
    echo "======================================"
    echo "[SUCCESS] Build fertig!"
    echo "======================================"
    echo ""
    
    if [ -d "dist/PDFExtractor.app" ]; then
        echo "Deine Datei: dist/PDFExtractor.app"
    else
        echo "Deine Datei: dist/PDFExtractor"
    fi
    
    echo "Du kannst diese Datei jetzt versenden!"
    echo ""
    open dist/
else
    echo ""
    echo "[FEHLER] Build fehlgeschlagen!"
    exit 1
fi
