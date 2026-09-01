# PDF Data Extractor by supersmart.at

**Befüllte PDF-Formulare auslesen → Daten sofort exportieren**

## Features

✅ Drag & Drop PDF-Upload  
✅ Passwortschutz (Admin-Funktion)  
✅ Multiple Export-Formate (CSV, JSON, Clipboard)  
✅ Keine Cloud, lokale Verarbeitung  
✅ Standalone Executable (ein Doppelklick)  

---

## Installation & Verwendung (für User)

### Windows / Mac
1. **Datei herunterladen:** `PDFExtractor.exe` oder `PDFExtractor.app`
2. **Doppelklick** → App öffnet sich
3. PDF reinschieben → Passwort eingeben → Extrahieren

**Passwort:** `admin123` (kann geändert werden, siehe unten)

---

## Für Developer: App selbst bauen

### Voraussetzungen
```bash
# Python 3.8+ installiert sein
python --version

# Abhängigkeiten installieren
pip install PyQt5 pypdf pyperclip
pip install pyinstaller
```

### Schritt 1: App testen (Python)
```bash
python pdf_extractor_app.py
```

Sollte ein Fenster öffnen mit:
- Drop-Zone für PDF
- Passwort-Input
- Radio-Buttons für Format
- Extract-Button

### Schritt 2: Executable erstellen (PyInstaller)

#### Windows:
```bash
pyinstaller --onefile --windowed --icon=icon.ico --name="PDFExtractor" pdf_extractor_app.py
```

Output: `dist/PDFExtractor.exe` (~50 MB)

#### Mac:
```bash
pyinstaller --onefile --windowed --icon=icon.icns --name="PDFExtractor" pdf_extractor_app.py
```

Output: `dist/PDFExtractor.app`

#### Linux:
```bash
pyinstaller --onefile --windowed --name="PDFExtractor" pdf_extractor_app.py
```

Output: `dist/PDFExtractor`

---

## Customization

### 1. Passwort ändern
In `pdf_extractor_app.py` Zeile 195:
```python
if password != "admin123":  # Hier ändern
```

### 2. Icon hinzufügen
```bash
# Icon als .ico (Windows) oder .icns (Mac) vorbereiten
# Dann PyInstaller aufrufen mit:
pyinstaller --onefile --windowed --icon=your_icon.ico --name="PDFExtractor" pdf_extractor_app.py
```

### 3. Branding anpassen
In `init_ui()` Methode (Zeile ~60):
```python
self.setWindowTitle("Dein Firmenname - PDF Extractor")
```

Und in der Info-Zeile (Zeile ~230):
```python
info = QLabel("© 2024 Deine Firma | Lokale Verarbeitung")
```

---

## Verbreitung

### Einfach:
1. `dist/PDFExtractor.exe` (oder `.app`) versenden
2. Fertig – User doppelklick

### Professionell:
- In einen Cloud-Drive packen (OneDrive, Google Drive)
- Mit Installationsanleitung und Support-Mail versenden
- Optional: Zip-Datei mit Dokumentation bündeln

---

## Troubleshooting

**"ModuleNotFoundError: No module named 'PyQt5'"**
```bash
pip install PyQt5
```

**"Das Programm kann nicht ausgeführt werden" (Windows)**
→ Eventuell Antivirensoftware blockiert. Ausnahme hinzufügen oder .exe-Datei signieren (kostet ~100€/Jahr)

**App startet nicht**
→ Terminal öffnen, `.exe` von dort aus starten um Fehlermeldung zu sehen:
```bash
cd dist/
PDFExtractor.exe
```

---

## Größe & Performance

| Aspekt | Wert |
|--------|------|
| Executable-Größe | ~50 MB |
| RAM bei Laufzeit | ~60–80 MB |
| Startup | ~1–2 Sekunden |
| PDF-Verarbeitung | ~0,5s pro Seite |

---

## Sicherheit

- ✅ Passwortgeschützt
- ✅ Keine Internetverbindung nötig
- ✅ Keine Cloud-Speicherung
- ✅ Lokale Dateiverarbeitung
- ⚠️ Passwort im Code sichtbar (wer Code liest) → Für höhere Sicherheit: Hash-Vergleich implementieren

---

## Roadmap / Ideen

- [ ] Batch-Verarbeitung (mehrere PDFs gleichzeitig)
- [ ] Datenbank-Export (SQLite, MySQL)
- [ ] E-Mail automatisiert versenden
- [ ] Feldmapping (PDF-Felder → Custom Spaltennamen)
- [ ] Verschlüsselte Passwort-Speicherung
- [ ] Dark Mode

---

## Support & Lizenz

**Autor:** supersmart.at  
**Lizenz:** MIT (frei verwendbar)  
**Support:** kontakt@supersmart.at

---

## Development-Tipps

### Code-Struktur
```
pdf_extractor_app.py
├── DropArea (Widget für Datei-Upload)
├── PDFExtractorApp (Hauptfenster)
│   ├── init_ui() (Interface)
│   ├── extract_data() (Verarbeitung)
│   └── _format_data() (Export-Formate)
└── main (__name__ == "__main__")
```

### Weitere PDF-Operationen (optional)
```python
# Im Code könnten auch hinzugefügt werden:
from PyPDF2 import PdfReader, PdfWriter

# - Mehrseiten-Verarbeitung
# - Text-Extraction zusätzlich
# - Signatur-Verifikation
# - Metadaten auslesen
```

### Build-Automatisierung (GitHub Actions)
```yaml
# .github/workflows/build.yml
name: Build Executables
on: [push]
jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install PyQt5 pypdf pyperclip pyinstaller
      - run: pyinstaller --onefile --windowed pdf_extractor_app.py
      - uses: actions/upload-artifact@v2
```

---

**Viel Erfolg! 🚀**
