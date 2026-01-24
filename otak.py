import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QUrl, QObject, pyqtSlot

# --- BAGIAN SARAF (LOGIKA BACKEND) ---
class Jembatan(QObject):
    @pyqtSlot(str)
    def terima_perintah(self, pesan):
        print(f"📡 DITERIMA: {pesan}")
        
        # Logika: Jika tombol OFF ditekan
        if pesan == "tutup_aplikasi":
            print("Mematikan Sistem...")
            sys.exit() # Tutup aplikasi

# --- BAGIAN UTAMA ---
app = QApplication(sys.argv)
browser = QWebEngineView()

# 1. Siapkan Jembatan
channel = QWebChannel()
handler = Jembatan()
channel.registerObject('jembatan_sistem', handler) # Nama ini penting!

# 2. Pasang Jembatan ke Browser
browser.page().setWebChannel(channel)

# 3. Muat HTML
path_sekarang = os.path.dirname(os.path.abspath(__file__))
path_html = os.path.join(path_sekarang, "aset/index.html")
browser.load(QUrl.fromLocalFile(path_html))

browser.showFullScreen()
sys.exit(app.exec())