import sys
import os
import psutil

# --- BLOKADE ERROR GRAFIS & GPU (WAJIB DI ATAS IMPORT PYQT) ---
# Mematikan akselerasi hardware agar tidak terjadi error gbm_wrapper di VirtualBox
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --no-sandbox --disable-software-rasterizer"
os.environ["QT_QUICK_BACKEND"] = "software"
os.environ["QT_XCB_GL_INTEGRATION"] = "none"

from PyQt6.QtCore import QUrl, QTimer, Qt, pyqtSlot, QObject
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel

# Kelas Jembatan: Menghubungkan Tombol di HTML ke Perintah Sistem Debian
class BackendSistem(QObject):
    @pyqtSlot()
    def matikan_sistem(self):
        """Perintah Shutdown Debian 12"""
        print("Siar Kota OS: Mematikan sistem...")
        os.system("sudo systemctl poweroff")

    @pyqtSlot()
    def mulai_ulang_sistem(self):
        """Perintah Reboot Debian 12"""
        print("Siar Kota OS: Memulai ulang sistem...")
        os.system("sudo systemctl reboot")

class SiarKotaOtak(QMainWindow):
    def __init__(self):
        super().__init__()

        # 1. Inisialisasi Browser Engine
        self.browser = QWebEngineView()
        
        # 2. Setup WebChannel (Jembatan Komunikasi Python-JS)
        self.channel = QWebChannel()
        self.backend = BackendSistem()
        self.channel.registerObject('backendSistem', self.backend)
        self.browser.page().setWebChannel(self.channel)

        # 3. Penentuan Jalur File dashboard.html di dalam folder 'aset'
        # Mengambil lokasi folder tempat otak.py berada
        base_dir = os.path.dirname(os.path.realpath(__file__))
        # Menggabungkan dengan sub-folder 'aset'
        path_html = os.path.join(base_dir, "aset", "dashboard.html")
        
        print(f"Memuat Antarmuka: {path_html}")
        
        if os.path.exists(path_html):
            self.browser.setUrl(QUrl.fromLocalFile(path_html))
        else:
            # Tampilan darurat jika file tidak ditemukan
            error_msg = f"<body style='background:black;color:red;padding:50px;'><h1>ERROR 404</h1><p>File tidak ditemukan di: {path_html}</p></body>"
            self.browser.setHtml(error_msg)

        # 4. Konfigurasi Jendela Kiosk
        self.setCentralWidget(self.browser)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint) # Menghilangkan border/bar atas
        self.showFullScreen() # Mode layar penuh

        # 5. Timer untuk Sinkronisasi Data Sensor (Interval 2 Detik)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data_sistem)
        self.timer.start(2000)

    def update_data_sistem(self):
        """Mengirim data CPU dan RAM asli ke Dashboard"""
        try:
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory().percent
            # Injeksi data ke fungsi updateMonitor() di dashboard.html
            js = f"if(typeof updateMonitor === 'function') {{ updateMonitor({cpu}, {ram}); }}"
            self.browser.page().runJavaScript(js)
        except Exception as e:
            print(f"Gagal memperbarui sensor: {e}")

if __name__ == "__main__":
    # Menjalankan aplikasi dengan argumen pelindung sandbox
    app = QApplication(sys.argv + ['--no-sandbox'])
    
    # Sembunyikan kursor agar tampilan bersih seperti Kiosk
    #app.setOverrideCursor(Qt.CursorShape.BlankCursor) 
    
    jendela_utama = SiarKotaOtak()
    jendela_utama.show()
    
    sys.exit(app.exec())