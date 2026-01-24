import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

# 1. Setup Aplikasi
app = QApplication(sys.argv)

# 2. Setup Browser
browser = QWebEngineView()

# 3. Tentukan Lokasi File HTML Lokal
# (Ini trik agar Python tahu di mana index.html berada secara otomatis)
path_sekarang = os.path.dirname(os.path.abspath(__file__))
path_html = os.path.join(path_sekarang, "aset/index.html")

# 4. Muat File HTML
browser.load(QUrl.fromLocalFile(path_html))

# 5. Tampilkan Full Screen
browser.showFullScreen()

# 6. Eksekusi
sys.exit(app.exec())
