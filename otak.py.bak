import sys
import os
import psutil
import subprocess
import shutil
import requests


# --- PERBAIKAN BLOKADE ERROR ---
# Hapus atau komentari baris QTWEBENGINE_REMOTE_DEBUGGING jika ada
if "QTWEBENGINE_REMOTE_DEBUGGING" in os.environ:
    del os.environ["QTWEBENGINE_REMOTE_DEBUGGING"]

# Gunakan level log 3 untuk menyembunyikan peringatan non-fatal
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
    "--disable-gpu --no-sandbox --disable-dev-shm-usage --disable-web-security --log-level=3"
)


os.environ["QT_QUICK_BACKEND"] = "software"
os.environ["QT_XCB_GL_INTEGRATION"] = "none"

from PyQt6.QtCore import QUrl, QTimer, Qt, pyqtSlot, QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel

# Import Saraf Modular
from saraf.saraf_catatan import CatatanSaraf
from saraf.saraf_berkas import BerkasSaraf

class TokoManager(QObject):
    appsChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.repo_raw_url = "https://github.com/Raviyanto/gudang-aplikasi-siar.git"
        self.base_path = os.path.dirname(os.path.realpath(__file__))
        self.apps_path = os.path.join(self.base_path, "aplikasi")
        self.window_ref = None # Akan diisi oleh SiarKotaOtak
        
        if not os.path.exists(self.apps_path):
            os.makedirs(self.apps_path)

    @pyqtSlot(str)
    def navigasi_langsung(self, url):
        """Membuka URL secara penuh untuk menghindari blokir iframe Google/YouTube"""
        if self.window_ref:
            self.window_ref.nav_bar.show() # Tampilkan bar sistem agar bisa kembali
            self.window_ref.browser.setUrl(QUrl(url))

    @pyqtSlot(result=list)
    def dapatkan_daftar_remote(self):
        url = "https://api.github.com/repos/Raviyanto/gudang-aplikasi-siar/contents/"
        try:
            res = requests.get(url, timeout=5)
            return [item["name"] for item in res.json() if item["type"] == "dir"] if res.status_code == 200 else []
        except:
            return []

    @pyqtSlot(result=list)
    def dapatkan_aplikasi_terinstal(self):
        return [d for d in os.listdir(self.apps_path) if os.path.isdir(os.path.join(self.apps_path, d))]

    @pyqtSlot(str, result=bool)
    def cek_terinstal(self, nama_app):
        return os.path.exists(os.path.join(self.apps_path, nama_app))

    @pyqtSlot(str)
    def instal_app(self, nama_app):
        try:
            os.chdir(self.apps_path)
            subprocess.run(f"git clone --depth 1 --filter=blob:none --sparse {self.repo_raw_url} {nama_app}_temp", shell=True, check=True)
            os.chdir(f"{nama_app}_temp")
            subprocess.run(f"git sparse-checkout set {nama_app}", shell=True, check=True)
            os.chdir(self.apps_path)
            shutil.move(f"{nama_app}_temp/{nama_app}", os.path.join(self.apps_path, nama_app))
            shutil.rmtree(f"{nama_app}_temp")
            self.appsChanged.emit()
        except Exception as e:
            print(f"Error Instal: {e}")

    @pyqtSlot(str)
    def hapus_app(self, nama_app):
        target = os.path.join(self.apps_path, nama_app)
        if os.path.exists(target):
            shutil.rmtree(target)
            self.appsChanged.emit()

    @pyqtSlot(str)
    def buka_aplikasi_siar(self, app_id):
        app_id = app_id.strip()
        if not self.window_ref: return

        # Jalur ke Dashboard
        if app_id == "dashboard":
            self.window_ref.nav_bar.hide()
            path = os.path.join(self.base_path, "aset", "dashboard.html")
            self.window_ref.browser.setUrl(QUrl.fromLocalFile(path))
            return

        # Jalur ke Toko Simpul
        if app_id == "toko_simpul":
            self.window_ref.nav_bar.hide()
            path = os.path.join(self.base_path, "aset", "toko.html")
            self.window_ref.browser.setUrl(QUrl.fromLocalFile(path))

        # Jalur ke Penjelajah (Upgrade: Membuka index.html penjelajah)
        elif app_id == "penjelajah":
            self.window_ref.nav_bar.hide() 
            path = os.path.join(self.apps_path, "penjelajah", "index.html")
            if os.path.exists(path):
                self.window_ref.browser.setUrl(QUrl.fromLocalFile(path))
            else:
                self.window_ref.nav_bar.show()
                self.window_ref.browser.setUrl(QUrl("https://www.google.com"))

        # Jalur ke Aplikasi Dinamis (Kalkulator, Manajer Berkas, Catatan)
        else:
            self.window_ref.nav_bar.hide()
            path = os.path.join(self.apps_path, app_id, "index.html")
            if os.path.exists(path):
                self.window_ref.browser.setUrl(QUrl.fromLocalFile(path))
            else:
                print(f"⚠️ Error: File tidak ditemukan di {path}")

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

        # 1. Inisialisasi Objek Backend
        self.toko = TokoManager()
        self.sistem = BackendSistem()
        self.catatan = CatatanSaraf()
        self.berkas = BerkasSaraf()
        
        # Beri referensi window ke TokoManager agar bisa kontrol navigasi
        self.toko.window_ref = self 

        # 2. Setup Layout Utama
        self.central_widget = QWidget()
        self.layout_utama = QVBoxLayout(self.central_widget)
        self.layout_utama.setContentsMargins(0, 0, 0, 0)
        self.layout_utama.setSpacing(0)
        self.setCentralWidget(self.central_widget)

        # 3. Bilah Navigasi Sistem (Muncul hanya saat browsing web luar)
        self.nav_bar = QWidget()
        self.nav_bar.setFixedHeight(50)
        self.nav_bar.setStyleSheet("background: #111; border-bottom: 2px solid #39ff14;")
        self.layout_nav = QHBoxLayout(self.nav_bar)

        self.url_input = QLineEdit()
        self.url_input.setStyleSheet("background: #222; border: 1px solid #39ff14; color: #39ff14; padding: 5px;")
        
        btn_kembali = QPushButton("◀ DASHBOARD")
        btn_kembali.setStyleSheet("background: #39ff14; color: #000; font-weight: bold; padding: 5px 15px;")
        btn_kembali.clicked.connect(self.kembali_ke_dashboard)

        self.layout_nav.addWidget(self.url_input)
        self.layout_nav.addWidget(btn_kembali)

        # 4. Setup Browser & Channel (URUTAN DIPERBAIKI)
        self.browser = QWebEngineView()
        self.channel = QWebChannel() 

        # DAFTARKAN SEMUA OBJEK KE CHANNEL
        self.channel.registerObject("tokoManager", self.toko)
        self.channel.registerObject("backendSistem", self.sistem)
        self.channel.registerObject("catatanSaraf", self.catatan)
        self.channel.registerObject("berkasSaraf", self.berkas)
        
        self.browser.page().setWebChannel(self.channel)

        # 5. Satukan ke Layout Utama
        self.layout_utama.addWidget(self.nav_bar)
        self.layout_utama.addWidget(self.browser)
        self.nav_bar.hide()

        # Load Dashboard Awal
        self.base_path = os.path.dirname(os.path.realpath(__file__))
        path_html = os.path.join(self.base_path, "aset", "dashboard.html")
        self.browser.setUrl(QUrl.fromLocalFile(path_html))

        # Fullscreen & Tanpa Frame (Mode Kiosk)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.showFullScreen()

        # Timer untuk Sensor Monitor
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_sensor)
        self.timer.start(2000)

    def kembali_ke_dashboard(self):
        self.toko.buka_aplikasi_siar('dashboard')

    def update_sensor(self):
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            js = f"if(typeof updateMonitor === 'function') {{ updateMonitor({cpu}, {ram}); }}"
            self.browser.page().runJavaScript(js)
        except: pass

if __name__ == "__main__":
    app = QApplication(sys.argv + ["--no-sandbox"])
    win = SiarKotaOtak()
    sys.exit(app.exec())
