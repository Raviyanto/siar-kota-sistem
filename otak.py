import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QUrl, QObject, pyqtSlot

# --- BAGIAN LOGIKA (SARAF) ---
class Jembatan(QObject):
    @pyqtSlot(str)
    def terima_perintah(self, pesan):
        print(f"📡 DITERIMA: {pesan}")
        
        if pesan == "tutup_aplikasi":
            print("🛑 SHUTDOWN AKTIF: Mematikan Sistem Operasi...")
            # PENTING: Tambahkan 'sudo' agar sistem menurut
            os.system("sudo systemctl poweroff")

# --- BAGIAN UTAMA ---
sys.argv.append("--disable-gpu")
sys.argv.append("--disable-software-rasterizer")

app = QApplication(sys.argv)
browser = QWebEngineView()

# Siapkan Jembatan
channel = QWebChannel()
handler = Jembatan()
channel.registerObject('jembatan_sistem', handler)
browser.page().setWebChannel(channel)

# Tentukan Lokasi File HTML
path_sekarang = os.path.dirname(os.path.abspath(__file__))
path_html = os.path.join(path_sekarang, "aset/dashboard.html")
browser.load(QUrl.fromLocalFile(path_html))

# Tampilkan
browser.showFullScreen()

# Jalankan Aplikasi
sys.exit(app.exec())
