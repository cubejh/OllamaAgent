import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTextEdit, QApplication
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from readPrompt import read_Prompt

# -----------------------------
# wait reply use Thread
# -----------------------------
class ReplyThread(QThread):
    finished = pyqtSignal(str)

    def __init__(self, user_input, cfg):
        super().__init__()
        self.user_input = user_input
        self.cfg = cfg

    def run(self):
        try:
            reply = read_Prompt(self.user_input, self.cfg)
        except Exception as e:
            reply = f"Error: {str(e)}"
        self.finished.emit(reply)


# -----------------------------
# Main Window
# -----------------------------
class OllamaChatUI(QMainWindow):
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        self.setWindowTitle("Ollama Chat UI")
        self.resize(600, 700)
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #EEE;
                font-size: 12pt;
            }

            QLineEdit, QTextEdit {
                background-color: #2e2e2e;
                color: #FFF;
                border: 1px solid #555;
                padding: 5px;
            }

            QPushButton {
                background-color: #3e3e3e;
                color: #FFF;
                border: 1px solid #666;
                border-radius: 5px;
                padding: 5px;
            }

            QPushButton:hover {
                background-color: #5e5e5e;
            }
        """)
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # Chat log
        self.chat_box = QTextEdit()
        self.chat_box.setReadOnly(True)
        self.chat_box.setFontFamily("Segoe UI Emoji")
        self.chat_box.setFontPointSize(12)
        main_layout.addWidget(self.chat_box)

        # Input row
        row = QHBoxLayout()
        self.entry = QLineEdit()
        self.entry.setPlaceholderText("Type message and press Enter or Send")
        self.entry.returnPressed.connect(self.send_message)
        row.addWidget(self.entry)

        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_message)
        row.addWidget(self.send_btn)

        main_layout.addLayout(row)

    def send_message(self):
        user_input = self.entry.text().strip()
        if not user_input:
            return
        self._insert_message(f"You: {user_input}", "#00ff00")
        self.entry.clear()

        self.thread = ReplyThread(user_input, self.cfg)
        self.thread.finished.connect(lambda reply: self._insert_message(f"Ollama: {reply}", "#00ffff"))
        self.thread.start()

    def _insert_message(self, text, color):
        self.chat_box.setTextColor(Qt.white)  
        self.chat_box.append(f'<span style="color:{color}">{text}</span>')
        self.chat_box.verticalScrollBar().setValue(self.chat_box.verticalScrollBar().maximum())


# -----------------------------
# connect outside
# -----------------------------
def run(cfg):
    """start UI"""
    app = QApplication(sys.argv)
    window = OllamaChatUI(cfg)
    window.show()
    sys.exit(app.exec_())
