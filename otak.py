import sys
import os
import psutil
import subprocess
import shutil
import requests

# === 1. KONFIGURASI MESIN CHROMIUM (STABILITAS & KEAMANAN) ===
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
try:
    from saraf.saraf_catatan import CatatanSaraf
    from saraf.saraf_berkas import BerkasSaraf
except ImportError:
    print("⚠️ Warning: Folder saraf atau file di dalamnya tidak ditemukan!")

class TokoManager(QObject):
    appsChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.repo_raw_url = "https://github.com/Raviyanto/gudang-aplikasi-siar.git"
        self.base_path = os.path.dirname(os.path.realpath(__file__))
        self.apps_path = os.path.join(self.base_path, "aplikasi")
        self.window_ref = None 
        
        if not os.path.exists(self.apps_path):
            os.makedirs(self.apps_path)

    @pyqtSlot(str)
    def navigasi_langsung(self, url):
        """Membuka URL secara penuh untuk menghindari blokir iframe"""
        if self.window_ref:
            self.window_ref.nav_bar.show()
            self.window_ref.browser.setUrl(QUrl(url))

    @pyqtSlot(str)
    def buka_aplikasi_siar(self, app_id):
        """Navigasi antar aplikasi internal Siar Kota"""
        app_id = app_id.strip()
        if not self.window_ref: return

        self.window_ref.nav_bar.hide()
        
        if app_id == "dashboard":
            path = os.path.join(self.base_path, "aset", "dashboard.html")
        elif app_id == "toko_simpul":
            path = os.path.join(self.base_path, "aset", "toko.html")
        else:
            path = os.path.join(self.apps_path, app_id, "index.html")

        if os.path.exists(path):
            self.window_ref.browser.setUrl(QUrl.fromLocalFile(path))
        else:
            print(f"⚠️ Error: Jalur {path} tidak ditemukan!")

    # --- Fitur Toko Simpul ---
    @pyqtSlot(result=list)
    def dapatkan_daftar_remote(self):
        url = "https://api.github.com/repos/Raviyanto/gudang-aplikasi-siar/contents/"
        try:
            res = requests.get(url, timeout=5)
            return [item["name"] for item in res.json() if item["type"] == "dir"] if res.status_code == 200 else []
        except: return []

    @pyqtSlot(result=list)
    def dapatkan_aplikasi_terinstal(self):
        return [d for d in os.listdir(self.apps_path) if os.path.isdir(os.path.join(self.apps_path, d))]

    @pyqtSlot(str)
    def instal_app(self, nama_app):
        try:
            os.chdir(self.apps_path)
            subprocess.run(f"git clone --depth 1 --filter=blob:none --sparse {self.repo_raw_url} {nama_app}_temp", shell=True)
            os.chdir(f"{nama_app}_temp")
            subprocess.run(f"git sparse-checkout set {nama_app}", shell=True)
            os.chdir(self.apps_path)
            shutil.move(f"{nama_app}_temp/{nama_app}", os.path.join(self.apps_path, nama_app))
            shutil.rmtree(f"{nama_app}_temp")
            self.appsChanged.emit()
        except Exception as e: print(f"Instal Error: {e}")

    @pyqtSlot(str)
    def hapus_app(self, nama_app):
        target = os.path.join(self.apps_path, nama_app)
        if os.path.exists(target):
            shutil.rmtree(target)
            self.appsChanged.emit()

class BackendSistem(QObject):
    @pyqtSlot()
    def matikan_sistem(self): os.system("sudo systemctl poweroff")
    @pyqtSlot()
    def mulai_ulang_sistem(self): os.system("sudo systemctl reboot")

class SiarKotaOtak(QMainWindow):
    def __init__(self):
        super().__init__()

        # 1. Inisialisasi Komponen Saraf
        self.toko = TokoManager()
        self.sistem = BackendSistem()
        self.catatan = CatatanSaraf()
        self.berkas = BerkasSaraf()
        self.toko.window_ref = self 

        # 2. Setup Antarmuka Dasar
        self.central_widget = QWidget()
        self.layout_utama = QVBoxLayout(self.central_widget)
        self.layout_utama.setContentsMargins(0, 0, 0, 0)
        self.layout_utama.setSpacing(0)
        self.setCentralWidget(self.central_widget)

        # 3. Bar Navigasi Sistem (Muncul saat Browsing Web Luar)
        self.nav_bar = QWidget()
        self.nav_bar.setFixedHeight(50)
        self.nav_bar.setStyleSheet("background: #000; border-bottom: 2px solid #39ff14;")
        layout_nav = QHBoxLayout(self.nav_bar)
        
        btn_back = QPushButton("◀ KEMBALI KE DASHBOARD")
        btn_back.setStyleSheet("background: #39ff14; color: #000; font-weight: bold; border: none; padding: 10px;")
        btn_back.clicked.connect(lambda: self.toko.buka_aplikasi_siar('dashboard'))
        layout_nav.addStretch()
        layout_nav.addWidget(btn_back)
        layout_nav.addStretch()

        # 4. Setup Browser & Channel Komunikasi
        self.browser = QWebEngineView()
        self.channel = QWebChannel()
        self.channel.registerObject("tokoManager", self.toko)
        self.channel.registerObject("backendSistem", self.sistem)
        self.channel.registerObject("catatanSaraf", self.catatan)
        self.channel.registerObject("berkasSaraf", self.berkas)
        self.browser.page().setWebChannel(self.channel)

        # 5. Injeksi Neon Hacker (Anti-Putih)
        self.browser.loadFinished.connect(self.suntik_gaya_neon)

        self.layout_utama.addWidget(self.nav_bar)
        self.layout_utama.addWidget(self.browser)
        self.nav_bar.hide()

        # Load Dashboard Awal
        self.base_path = os.path.dirname(os.path.realpath(__file__))
        self.browser.setUrl(QUrl.fromLocalFile(os.path.join(self.base_path, "aset", "dashboard.html")))

        # Mode Kiosk
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.showFullScreen()

        # Timer Sensor Monitor CPU/RAM
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_sensor)
        self.timer.start(2000)

    def suntik_gaya_neon(self):
        """Memaksa semua situs web menjadi hitam & neon"""
        js_code = """
        (function() {
            var style = document.createElement('style');
            style.innerHTML = `
                html, body, div:not([id*="player"]), section, nav, header, footer { 
                    background-color: #000000 !important; 
                    color: #39ff14 !important; 
                }
                h1, h2, h3, h4, h5, h6, p, span, a, em, cite { 
                    color: #39ff14 !important; 
                    text-shadow: 0 0 2px rgba(57, 255, 20, 0.5) !important;
                }
                a { color: #39ff14 !important; text-decoration: underline; }
                input, textarea { 
                    background: #111 !important; border: 1px solid #39ff14 !important; color: #39ff14 !important; 
                }
                /* Invert gambar/logo agar tidak silau */
                img, .logo, svg { filter: brightness(0.8) contrast(1.2) grayscale(0.5); }
            `;
            document.head.appendChild(style);
        })()
        """
        self.browser.page().runJavaScript(js_code)

    def update_sensor(self):
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            self.browser.page().runJavaScript(f"if(typeof updateMonitor === 'function') {{ updateMonitor({cpu}, {ram}); }}")
        except: pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SiarKotaOtak()
    sys.exit(app.exec())
