#!/usr/bin/env python3
import sys
import hashlib
import string
import time
import threading
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QSpinBox, QPushButton, QTextEdit, QCheckBox,
    QGroupBox, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QColor

class Worker(QObject):
    progress = pyqtSignal(str)
    current_progress = pyqtSignal(str)
    finished = pyqtSignal(str, int, int, str)

    def run_bruteforce(self, target_hash, salt, length, charset):
        def index_to_candidate(idx, length, charset):
            charset_len = len(charset)
            candidate_chars = []
            for _ in range(length):
                candidate_chars.append(charset[idx % charset_len])
                idx //= charset_len
            return ''.join(reversed(candidate_chars))

        total_attempts_estimate = len(charset) ** length
        
        start_time = time.time()
        attempts = 0
        last_report = time.time()
        
        for idx in range(total_attempts_estimate):
            candidate_str = index_to_candidate(idx, length, charset)
            attempts += 1
            
            inner_hash = hashlib.sha256(candidate_str.encode()).hexdigest()
            combined = inner_hash + salt
            current_hash = hashlib.sha256(combined.encode()).hexdigest()
            
            now = time.time()
            if now - last_report >= 0.5:
                elapsed = now - start_time
                speed = attempts / max(elapsed, 0.001)
                self.current_progress.emit(f"Attempt: {attempts:,} | Speed: {int(speed):,} hash/s | Current: {candidate_str}")
                last_report = now
            
            if current_hash == target_hash:
                elapsed = int(time.time() - start_time)
                self.finished.emit('found', attempts, elapsed, candidate_str)
                return
        
        self.finished.emit('not_found', 0, 0, '')


class GETHASHApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.running = False
        self.worker_thread = None
        self.worker = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("HashCracker")
        self.setGeometry(100, 100, 550, 500)
        self.setMinimumWidth(500)
        self.setMinimumHeight(450)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(8)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title = QLabel("HashCracker")
        title_font = QFont("Arial", 18, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #f59e0b;")
        layout.addWidget(title)
        
        hash_label = QLabel("SHA-256 Hash:")
        hash_label.setStyleSheet("font-weight: bold; color: #333; font-size: 11px;")
        layout.addWidget(hash_label)
        self.hash_input = QLineEdit()
        self.hash_input.setStyleSheet("""
            QLineEdit {
                padding: 6px;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
                color: #333;
                font-family: 'Monaco', 'Courier New', monospace;
                font-size: 10px;
            }
            QLineEdit:focus {
                border: 2px solid #f59e0b;
            }
        """)
        self.hash_input.setMaximumHeight(28)
        layout.addWidget(self.hash_input)
        
        salt_label = QLabel("Salt:")
        salt_label.setStyleSheet("font-weight: bold; color: #333; font-size: 11px;")
        layout.addWidget(salt_label)
        self.salt_input = QLineEdit()
        self.salt_input.setStyleSheet("""
            QLineEdit {
                padding: 6px;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
                color: #333;
                font-family: 'Monaco', 'Courier New', monospace;
                font-size: 10px;
            }
            QLineEdit:focus {
                border: 2px solid #f59e0b;
            }
        """)
        self.salt_input.setMaximumHeight(28)
        layout.addWidget(self.salt_input)
        
        length_layout = QHBoxLayout()
        length_label = QLabel("Length:")
        length_label.setStyleSheet("font-weight: bold; color: #333; font-size: 11px;")
        length_layout.addWidget(length_label)
        self.length_input = QSpinBox()
        self.length_input.setMinimum(1)
        self.length_input.setMaximum(12)
        self.length_input.setValue(6)
        self.length_input.setStyleSheet("""
            QSpinBox {
                padding: 4px;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
                color: #333;
                width: 60px;
                font-size: 10px;
            }
            QSpinBox:focus {
                border: 2px solid #f59e0b;
            }
        """)
        self.length_input.setMaximumHeight(26)
        length_layout.addWidget(self.length_input)
        length_layout.addStretch()
        layout.addLayout(length_layout)
        
        charset_label = QLabel("Charset:")
        charset_label.setStyleSheet("font-weight: bold; color: #333; font-size: 11px;")
        layout.addWidget(charset_label)
        
        charset_group = QGroupBox()
        charset_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                margin: 2px 0px 8px 0px;
                padding-top: 6px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 2px 0 2px;
            }
        """)
        charset_layout = QVBoxLayout()
        charset_layout.setSpacing(3)
        charset_layout.setContentsMargins(5, 3, 5, 5)
        
        self.charset_checks = {}
        charsets = [
            ('1', 'a-z', string.ascii_lowercase),
            ('2', 'A-Z', string.ascii_uppercase),
            ('3', '0-9', string.digits),
            ('4', 'All', string.ascii_letters + string.digits + string.punctuation),
            ('5', 'Letters', string.ascii_letters),
            ('6', 'Alphanumeric', string.ascii_letters + string.digits),
        ]
        
        for key, label, charset in charsets:
            cb = QCheckBox(label)
            cb.setStyleSheet("""
                QCheckBox {
                    color: #333;
                    padding: 2px;
                    font-size: 11px;
                    spacing: 5px;
                }
                QCheckBox::indicator {
                    width: 14px;
                    height: 14px;
                    border: 1px solid #f59e0b;
                    border-radius: 2px;
                    background-color: white;
                }
                QCheckBox::indicator:checked {
                    background-color: #f59e0b;
                }
            """)
            self.charset_checks[key] = cb
            charset_layout.addWidget(cb)
        
        charset_group.setLayout(charset_layout)
        layout.addWidget(charset_group)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(6)
        
        self.start_btn = QPushButton("START")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #f59e0b;
                color: white;
                font-weight: bold;
                padding: 8px;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #d97706;
            }
            QPushButton:pressed {
                background-color: #b45309;
            }
        """)
        self.start_btn.setMaximumHeight(32)
        self.start_btn.clicked.connect(self.start_attack)
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("STOP")
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                font-weight: bold;
                padding: 8px;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
            QPushButton:pressed {
                background-color: #b91c1c;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.stop_btn.setMaximumHeight(32)
        self.stop_btn.clicked.connect(self.stop_attack)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)
        
        self.clear_btn = QPushButton("CLEAR")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #6b7280;
                color: white;
                font-weight: bold;
                padding: 8px;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        self.clear_btn.setMaximumHeight(32)
        self.clear_btn.clicked.connect(self.clear_all)
        button_layout.addWidget(self.clear_btn)
        
        layout.addLayout(button_layout)
        
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont("Monaco", 10))
        self.output.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                border: 2px solid #f59e0b;
                border-radius: 4px;
                padding: 8px;
                color: #00ff00;
                font-family: 'Monaco', 'Courier New', monospace;
                font-size: 10px;
            }
        """)
        self.output.setMaximumHeight(70)
        layout.addWidget(self.output)
        
        central.setStyleSheet("QWidget { background-color: white; }")

    def get_charset(self):
        charset_map = {
            '1': string.ascii_lowercase,
            '2': string.ascii_uppercase,
            '3': string.digits,
            '4': string.ascii_letters + string.digits + string.punctuation,
            '5': string.ascii_letters,
            '6': string.ascii_letters + string.digits,
        }
        
        charset = ""
        for key, cb in self.charset_checks.items():
            if cb.isChecked():
                if key in ['5', '6']:
                    charset = charset_map[key]
                    break
                else:
                    charset += charset_map[key]
        
        return charset if charset else string.ascii_lowercase

    def log(self, message):
        self.output.append(message)

    def update_current(self, message):
        parts = message.split(' | ')
        if len(parts) >= 3:
            self.output.setPlainText(message)

    def start_attack(self):
        target_hash = self.hash_input.text().strip().lower()
        salt = self.salt_input.text().strip()
        length = self.length_input.value()
        
        if not target_hash or not salt:
            self.log("ERROR: Enter Hash and Salt")
            return
        
        charset = self.get_charset()
        
        self.output.clear()
        
        self.running = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        self.worker = Worker()
        self.worker.progress.connect(self.log)
        self.worker.current_progress.connect(self.update_current)
        self.worker.finished.connect(self.on_finished)
        
        self.worker_thread = threading.Thread(
            target=self.worker.run_bruteforce,
            args=(target_hash, salt, length, charset)
        )
        self.worker_thread.daemon = True
        self.worker_thread.start()

    def on_finished(self, status, attempts, elapsed, password):
        if status == 'found':
            self.output.clear()
            self.output.append("FOUND!")
            self.output.append(f"Password: {password}")
            self.output.append(f"Attempts: {attempts:,}")
            self.output.append(f"Time: {elapsed}s")
        else:
            self.output.clear()
            self.output.append("NOT FOUND")
        
        self.running = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def stop_attack(self):
        self.running = False
        self.log("")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def clear_all(self):
        self.hash_input.clear()
        self.salt_input.clear()
        self.length_input.setValue(6)
        for cb in self.charset_checks.values():
            cb.setChecked(False)
        self.output.clear()


def main():
    app = QApplication(sys.argv)
    window = GETHASHApp()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()