import sys
import os
import psutil
from PyQt6.QtCore import QUrl, QTimer, Qt, pyqtSlot, QObject
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel

# Jembatan Komunikasi: Python -> HTML
class BackendSistem(QObject):
    @pyqtSlot()
    def matikan_sistem(self):
        """Mematikan Debian 12"""
        os.system("systemctl poweroff")

    @pyqtSlot()
    def mulai_ulang_sistem(self):
        """Reboot Debian 12"""
        os.system("systemctl reboot")

class SiarKotaOtak(QMainWindow):
    def __init__(self):
        super().__init__()

        # Inisialisasi Browser
        self.browser = QWebEngineView()
        
        # Setup Saluran Komunikasi (WebChannel)
        self.channel = QWebChannel()
        self.backend = BackendSistem()
        self.channel.registerObject('backendSistem', self.backend)
        self.browser.page().setWebChannel(self.channel)

        # Memuat Dashboard Lokal
        path_html = os.path.abspath("dashboard.html")
        self.browser.setUrl(QUrl.fromLocalFile(path_html))

        # Konfigurasi Tampilan Kiosk
        self.setCentralWidget(self.browser)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.showFullScreen()

        # Timer untuk Sinkronisasi Sensor (Setiap 2 Detik)
        self.timer = QTimer()
        self.timer.timeout.connect(self.perbarui_sensor)
        self.timer.start(2000)

    def perbarui_sensor(self):
        """Mengirim data CPU/RAM ke Dashboard"""
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            # Menyuntikkan JavaScript ke halaman yang sedang berjalan
            script = f"if(typeof updateMonitor === 'function') {{ updateMonitor({cpu}, {ram}); }}"
            self.browser.page().runJavaScript(script)
        except Exception as e:
            print(f"Sensor Error: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Sembunyikan kursor agar terlihat seperti OS tertanam
    app.setOverrideCursor(Qt.CursorShape.BlankCursor) 
    
    mesin = SiarKotaOtak()
    mesin.show()
    sys.exit(app.exec())