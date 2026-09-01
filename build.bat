@echo off
REM PDF Extractor Build Script für Windows
REM Dieses Skript baut die .exe Datei automatisch

echo ======================================
echo PDF Extractor - Build Script
echo ======================================
echo.

REM Prüfe ob PyInstaller installiert ist
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] PyInstaller nicht installiert!
    echo Bitte ausführen: pip install pyinstaller
    pause
    exit /b 1
)

echo [1/3] Räume alte Build auf...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
del /q pdf_extractor_app.spec 2>nul

echo [2/3] Baue Executable...
REM Mit Icon (wenn vorhanden)
if exist icon.ico (
    pyinstaller --onefile --windowed --icon=icon.ico --name="PDFExtractor" pdf_extractor_app.py
) else (
    echo [HINWEIS] icon.ico nicht gefunden - wird ohne Icon gebaut
    pyinstaller --onefile --windowed --name="PDFExtractor" pdf_extractor_app.py
)

echo [3/3] Aufräumen...
rmdir /s /q build
del /q pdf_extractor_app.spec

if exist dist\PDFExtractor.exe (
    echo.
    echo ======================================
    echo [SUCCESS] Build fertig!
    echo ======================================
    echo.
    echo Deine Datei: dist\PDFExtractor.exe (~50 MB)
    echo Du kannst diese Datei jetzt versenden!
    echo.
    echo Öffne dist\ Ordner:
    start dist
) else (
    echo.
    echo [FEHLER] Build fehlgeschlagen!
    pause
    exit /b 1
)

pause
