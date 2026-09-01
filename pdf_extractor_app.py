#!/usr/bin/env python3
"""
PDF Data Extractor by supersmart.at
Extrahiert Formularfelder aus befüllbaren PDFs mit Passwortschutz
"""

import sys
import json
import csv
import webbrowser
import urllib.parse
from pathlib import Path
from io import StringIO
from datetime import datetime
import pyperclip
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QLabel, QLineEdit, QPushButton, QRadioButton, QButtonGroup,
    QTextEdit, QMessageBox, QFileDialog, QDialog, QCheckBox
)
from PyQt5.QtCore import Qt, QMimeData, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QIcon
from PyQt5.QtCore import QEventLoop, QTimer
from pypdf import PdfReader


class DropArea(QWidget):
    """Drag-and-Drop Zone für PDF"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pdf_path = None
        self.setAcceptDrops(True)
        self.setStyleSheet("""
            QWidget {
                border: 2px dashed #999;
                border-radius: 5px;
                background-color: #f9f9f9;
                min-height: 100px;
            }
        """)
        
        layout = QVBoxLayout()
        self.label = QLabel("📄 PDF hier reinschieben...\noder klicken zum Durchsuchen")
        self.label.setAlignment(Qt.AlignCenter)
        font = self.label.font()
        font.setPointSize(11)
        self.label.setFont(font)
        layout.addWidget(self.label)
        self.setLayout(layout)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
            self.setStyleSheet("""
                QWidget {
                    border: 2px solid #FF6600;
                    border-radius: 5px;
                    background-color: #fff3e0;
                    min-height: 100px;
                }
            """)
        else:
            event.ignore()
    
    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QWidget {
                border: 2px dashed #999;
                border-radius: 5px;
                background-color: #f9f9f9;
                min-height: 100px;
            }
        """)
    
    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        pdf_files = [f for f in files if f.endswith('.pdf')]
        
        if pdf_files:
            self.pdf_path = pdf_files[0]
            filename = Path(self.pdf_path).name
            self.label.setText(f"✓ {filename}")
            self.setStyleSheet("""
                QWidget {
                    border: 2px solid #4CAF50;
                    border-radius: 5px;
                    background-color: #f1f8f5;
                    min-height: 100px;
                }
            """)
        else:
            QMessageBox.warning(self, "Fehler", "Bitte nur PDF-Dateien!")
    
    def mousePressEvent(self, event):
        """Öffne Datei-Dialog beim Klick"""
        file, _ = QFileDialog.getOpenFileName(
            self, "PDF wählen", "", "PDF Files (*.pdf)"
        )
        if file:
            self.pdf_path = file
            filename = Path(file).name
            self.label.setText(f"✓ {filename}")
            self.setStyleSheet("""
                QWidget {
                    border: 2px solid #4CAF50;
                    border-radius: 5px;
                    background-color: #f1f8f5;
                    min-height: 100px;
                }
            """)


class FeedbackDialog(QDialog):
    """
    Feedback-Dialog nach erfolgreicher PDF-Extraktion.
    Sammelt strukturierte Fragen, generiert mailto-Link mit Pre-Fill.
    """
    
    feedback_submitted = pyqtSignal(dict)
    
    def __init__(self, extraction_results=None, pdf_filename="", parent=None):
        super().__init__(parent)
        self.extraction_results = extraction_results or {}
        self.pdf_filename = pdf_filename
        self.user_answers = {}
        
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Feedback & Weiterentwicklung")
        self.setGeometry(100, 100, 480, 400)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QLabel("Feedback & Weiterentwicklung")
        header_font = header.font()
        header_font.setPointSize(13)
        header_font.setBold(True)
        header.setFont(header_font)
        layout.addWidget(header)
        
        # Intro text
        intro = QLabel(
            "Dieses Tool ist kostenlos. Aber wir würden gerne wissen, "
            "ob es bei dir funktioniert:"
        )
        intro.setWordWrap(True)
        intro.setStyleSheet("color: #666;")
        layout.addWidget(intro)
        
        layout.addSpacing(12)
        
        # Question 1: Works?
        self.cb_works = QCheckBox("Funktioniert es mit deinen Formularen?")
        layout.addWidget(self.cb_works)
        
        layout.addSpacing(6)
        
        # Question 2: PDF Software
        label_software = QLabel("Welche PDF-Software nutzt du?")
        layout.addWidget(label_software)
        
        self.input_software = QLineEdit()
        self.input_software.setPlaceholderText("z.B. LibreOffice, Adobe, Kirby, etc.")
        layout.addWidget(self.input_software)
        
        layout.addSpacing(6)
        
        # Question 3: Improvements
        label_improvements = QLabel("Was könnte besser sein?")
        layout.addWidget(label_improvements)
        
        self.textarea_improvements = QTextEdit()
        self.textarea_improvements.setPlaceholderText("Dein Feedback hilft uns...")
        self.textarea_improvements.setMaximumHeight(80)
        layout.addWidget(self.textarea_improvements)
        
        layout.addSpacing(12)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        later_btn = QPushButton("Später")
        later_btn.clicked.connect(self.reject)
        button_layout.addWidget(later_btn)
        
        send_btn = QPushButton("Feedback geben →")
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF6600;
                color: white;
                padding: 8px;
                font-weight: bold;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #E85A00;
            }
        """)
        send_btn.clicked.connect(self.send_feedback)
        button_layout.addWidget(send_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def collect_answers(self):
        """Sammelt alle Antworten aus den Widgets."""
        answers = {
            "timestamp": datetime.now().isoformat(),
            "pdf_filename": self.pdf_filename,
            "extracted_fields": len(self.extraction_results),
            "works": self.cb_works.isChecked(),
            "pdf_software": self.input_software.text(),
            "improvements": self.textarea_improvements.toPlainText(),
        }
        return answers
    
    def generate_mailto_link(self, answers):
        """Generiert einen mailto-Link mit formatiertem Body."""
        
        plain_body = f"""Hallo Andreas,

Feedback zum PDF-Extractor
Datum: {answers['timestamp']}
PDF-Datei: {answers['pdf_filename']}
Erkannte Felder: {answers['extracted_fields']}

Funktioniert: {('Ja' if answers.get('works') else 'Nein')}

PDF-Software: {answers.get('pdf_software', '')}

Feedback:
{answers.get('improvements', '')}

Viele Grüße"""
        
        # URL-encode
        subject = "Feedback: PDF-Extractor Test"
        mailto_link = f"mailto:andreas@supersmart.at?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(plain_body)}"
        
        return mailto_link, plain_body
    
    def send_feedback(self):
        """Sammelt Feedback, generiert mailto-Link, öffnet Mail-Client."""
        answers = self.collect_answers()
        self.user_answers = answers
        
        mailto_link, plain_body = self.generate_mailto_link(answers)
        
        # Öffne Mail-Client
        webbrowser.open(mailto_link)
        
        # Zeige Danke-Dialog
        self.show_thank_you_dialog()
    
    def show_thank_you_dialog(self):
        """Zeigt 'Danke'-Dialog nach Mailto-Öffnung."""
        thank_you = ThankYouDialog(parent=self)
        thank_you.closed.connect(self.accept)
        thank_you.exec_()


class ThankYouDialog(QDialog):
    """Danke-Dialog mit 'Tool verwenden' CTA."""
    
    closed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Danke!")
        self.setGeometry(100, 100, 420, 250)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # Success message
        header = QLabel("✓ Danke!")
        header_font = header.font()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header.setFont(header_font)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        message = QLabel(
            "Deine Nachricht wurde vorbereitet.\n"
            "Bitte sende sie ab — danke!"
        )
        message.setWordWrap(True)
        message.setAlignment(Qt.AlignCenter)
        message.setStyleSheet("color: #666;")
        layout.addWidget(message)
        
        layout.addSpacing(12)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        close_btn = QPushButton("Fenster ✕")
        close_btn.clicked.connect(self.reject)
        button_layout.addWidget(close_btn)
        
        continue_btn = QPushButton("Tool verwenden →")
        continue_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF6600;
                color: white;
                padding: 8px;
                font-weight: bold;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #E85A00;
            }
        """)
        continue_btn.clicked.connect(self.accept)
        button_layout.addWidget(continue_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def accept(self):
        """Tool-Fenster wird fokussiert, Dialoge schließen sich."""
        self.closed.emit()
        super().accept()


class PDFExtractorApp(QMainWindow):
    """Hauptanwendung"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Erstelle GUI"""
        self.setWindowTitle("PDF Data Extractor by supersmart.at")
        self.setGeometry(100, 100, 600, 700)
        
        # Zentrales Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Titel
        title = QLabel("PDF Formular-Daten Extractor")
        font = title.font()
        font.setPointSize(14)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Befüllte PDFs auslesen → Daten exportieren")
        subtitle_font = subtitle.font()
        subtitle_font.setPointSize(9)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet("color: #666;")
        layout.addWidget(subtitle)
        
        # Drop Area
        layout.addWidget(QLabel("Schritt 1: PDF laden"))
        self.drop_area = DropArea()
        layout.addWidget(self.drop_area)
        
        # Passwort
        layout.addWidget(QLabel("Schritt 2: Admin-Passwort"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Passwort eingeben...")
        layout.addWidget(self.password_input)
        
        # Export-Format
        layout.addWidget(QLabel("Schritt 3: Export-Format"))
        
        format_layout = QVBoxLayout()
        self.format_group = QButtonGroup()
        
        formats = [
            ("CSV (für Excel)", "csv"),
            ("JSON (für Integration)", "json"),
            ("Zwischenablage (copy)", "copy"),
        ]
        
        for i, (label_text, value) in enumerate(formats):
            radio = QRadioButton(label_text)
            radio.setProperty("format", value)
            if i == 0:
                radio.setChecked(True)
            self.format_group.addButton(radio, i)
            format_layout.addWidget(radio)
        
        layout.addLayout(format_layout)
        
        # Output-Bereich
        layout.addWidget(QLabel("Ergebnis:"))
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMaximumHeight(150)
        layout.addWidget(self.output_text)
        
        # Button
        button_layout = QHBoxLayout()
        self.extract_button = QPushButton("→ EXTRAHIEREN")
        self.extract_button.setStyleSheet("""
            QPushButton {
                background-color: #FF6600;
                color: white;
                padding: 10px;
                font-size: 12pt;
                font-weight: bold;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #E85A00;
            }
            QPushButton:pressed {
                background-color: #CC4C00;
            }
        """)
        self.extract_button.setCursor(Qt.PointingHandCursor)
        self.extract_button.clicked.connect(self.extract_data)
        button_layout.addWidget(self.extract_button)
        
        # Copy Button
        self.copy_button = QPushButton("📋 Kopieren")
        self.copy_button.setEnabled(False)
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        button_layout.addWidget(self.copy_button)
        
        # Save Button
        self.save_button = QPushButton("💾 Speichern")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_to_file)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        
        # Info
        info = QLabel("© 2024 supersmart.at | Lokale Verarbeitung • Kein Cloud Upload")
        info_font = info.font()
        info_font.setPointSize(8)
        info.setFont(info_font)
        info.setStyleSheet("color: #999; text-align: center;")
        layout.addWidget(info)
        
        layout.addStretch()
    
    def extract_data(self):
        """Extrahiere PDF-Daten"""
        
        # Validierung
        if not self.drop_area.pdf_path:
            QMessageBox.warning(self, "Fehler", "Bitte PDF laden!")
            return
        
        password = self.password_input.text()
        if password != "admin123":  # Beispiel-Passwort
            QMessageBox.warning(self, "Fehler", "Falsches Passwort!")
            self.password_input.clear()
            return
        
        try:
            # PDF lesen
            reader = PdfReader(self.drop_area.pdf_path)
            fields = reader.get_fields()
            
            if not fields:
                QMessageBox.warning(self, "Fehler", "Keine Formularfelder in PDF!")
                return
            
            # Format bestimmen
            selected_radio = self.format_group.checkedButton()
            export_format = selected_radio.property("format")
            
            # Daten verarbeiten
            self.extracted_data = self._format_data(fields, export_format)
            self.output_text.setText(self.extracted_data)
            
            # Buttons aktivieren
            self.copy_button.setEnabled(True)
            self.save_button.setEnabled(True)
            
            # Feedback-Dialog zeigen
            pdf_filename = Path(self.drop_area.pdf_path).name
            feedback_dialog = FeedbackDialog(
                extraction_results=fields,
                pdf_filename=pdf_filename,
                parent=self
            )
            feedback_dialog.exec_()
            
            QMessageBox.information(self, "Erfolg", "Daten extrahiert!")
            
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Extrahieren:\n{str(e)}")
    
    def _format_data(self, fields, format_type):
        """Formatiere Daten je nach Typ"""
        
        if format_type == "csv":
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(["Feldname", "Wert"])
            for name, field_data in fields.items():
                value = field_data.get("/V", "") if isinstance(field_data, dict) else field_data
                writer.writerow([name, value])
            return output.getvalue()
        
        elif format_type == "json":
            data = {}
            for name, field_data in fields.items():
                value = field_data.get("/V", "") if isinstance(field_data, dict) else field_data
                data[name] = value
            return json.dumps(data, indent=2, ensure_ascii=False)
        
        else:  # copy
            lines = []
            for name, field_data in fields.items():
                value = field_data.get("/V", "") if isinstance(field_data, dict) else field_data
                lines.append(f"{name}: {value}")
            return "\n".join(lines)
    
    def copy_to_clipboard(self):
        """Kopiere Ausgabe in Zwischenablage"""
        try:
            pyperclip.copy(self.output_text.toPlainText())
            QMessageBox.information(self, "Erfolg", "In Zwischenablage kopiert!")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler: {str(e)}")
    
    def save_to_file(self):
        """Speichere Ausgabe in Datei"""
        try:
            selected_radio = self.format_group.checkedButton()
            export_format = selected_radio.property("format")
            
            ext_map = {"csv": "*.csv", "json": "*.json", "copy": "*.txt"}
            ext = ext_map.get(export_format, "*.txt")
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Speichern unter", "", f"Files ({ext})"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.output_text.toPlainText())
                QMessageBox.information(self, "Erfolg", f"Gespeichert: {file_path}")
        
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFExtractorApp()
    window.show()
    sys.exit(app.exec_())
