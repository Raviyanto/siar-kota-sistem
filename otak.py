import sys
import os
import psutil
import subprocess
import shutil
import requests

# --- KONFIGURASI STABILITAS VIRTUALBOX ---
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --no-sandbox"
os.environ["QT_QUICK_BACKEND"] = "software"

from PyQt6.QtCore import QUrl, QTimer, Qt, pyqtSlot, QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel

class TokoManager(QObject):
    # Sinyal untuk memberitahu Dashboard agar refresh ikon
    appsChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.repo_api_url = "https://api.github.com/repos/Raviyanto/gudang-aplikasi-siar/contents/"
        self.repo_raw_url = "https://github.com/Raviyanto/gudang-aplikasi-siar.git"
        self.base_path = os.path.dirname(os.path.realpath(__file__))
        self.apps_path = os.path.join(self.base_path, "aplikasi")
        
        if not os.path.exists(self.apps_path):
            os.makedirs(self.apps_path)

    @pyqtSlot(result=list)
    def dapatkan_daftar_remote(self):
        """Ambil daftar dari GitHub API"""
        try:
            res = requests.get(self.repo_api_url, timeout=5)
            if res.status_code == 200:
                return [item['name'] for item in res.json() if item['type'] == 'dir']
            return []
        except: return []

    @pyqtSlot(result=list)
    def dapatkan_aplikasi_terinstal(self):
        """Memindai folder aplikasi/ secara real-time"""
        if not os.path.exists(self.apps_path): return []
        # Mengambil daftar folder di direktori aplikasi/
        return [d for d in os.listdir(self.apps_path) if os.path.isdir(os.path.join(self.apps_path, d))]

    @pyqtSlot(str)
    def instal_app(self, nama_app):
        """Proses Git Clone ke folder lokal"""
        target_dir = os.path.join(self.apps_path, nama_app)
        if os.path.exists(target_dir): return

        try:
            print(f"Siar Kota OS: Mengunduh {nama_app}...")
            # Proses Sparse Checkout agar hemat ruang
            os.chdir(self.apps_path)
            subprocess.run(f"git clone --depth 1 --filter=blob:none --sparse {self.repo_raw_url} {nama_app}_temp", shell=True, check=True)
            os.chdir(f"{nama_app}_temp")
            subprocess.run(f"git sparse-checkout set {nama_app}", shell=True, check=True)
            os.chdir(self.apps_path)
            shutil.move(f"{nama_app}_temp/{nama_app}", target_dir)
            shutil.rmtree(f"{nama_app}_temp")
            
            print(f"Siar Kota OS: {nama_app} Terpasang.")
            self.appsChanged.emit() # Beritahu Dashboard!
        except Exception as e:
            print(f"Gagal Instal: {e}")

    @pyqtSlot(str)
    def hapus_app(self, nama_app):
        target = os.path.join(self.apps_path, nama_app)
        if os.path.exists(target):
            shutil.rmtree(target)
            print(f"Siar Kota OS: {nama_app} Dihapus.")
            self.appsChanged.emit() # Beritahu Dashboard!

class BackendSistem(QObject):
    @pyqtSlot()
    def matikan_sistem(self):
        os.system("sudo systemctl poweroff")
    @pyqtSlot()
    def mulai_ulang_sistem(self):
        os.system("sudo systemctl reboot")

class SiarKotaOtak(QMainWindow):
    def __init__(self):
        super().__init__()
        self.browser = QWebEngineView()
        self.channel = QWebChannel()
        self.toko = TokoManager()
        self.sistem = BackendSistem()
        
        self.channel.registerObject('tokoManager', self.toko)
        self.channel.registerObject('backendSistem', self.sistem)
        self.browser.page().setWebChannel(self.channel)

        base_dir = os.path.dirname(os.path.realpath(__file__))
        path_html = os.path.join(base_dir, "aset", "dashboard.html")
        self.browser.setUrl(QUrl.fromLocalFile(path_html))

        self.setCentralWidget(self.browser)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.showFullScreen()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_sensor)
        self.timer.start(2000)

    def update_sensor(self):
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            js = f"if(typeof updateMonitor === 'function') {{ updateMonitor({cpu}, {ram}); }}"
            self.browser.page().runJavaScript(js)
        except: pass

if __name__ == "__main__":
    app = QApplication(sys.argv + ['--no-sandbox'])
    # app.setOverrideCursor(Qt.CursorShape.BlankCursor) 
    win = SiarKotaOtak()
    win.show()
    sys.exit(app.exec())