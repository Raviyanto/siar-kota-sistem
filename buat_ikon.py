import os
from PIL import Image, ImageDraw

# Konfigurasi Warna Siar Kota
NEON_GREEN = (57, 255, 20, 255) # #39ff14
BLACK = (0, 0, 0, 255)
SIZE = (200, 200)

def buat_ikon_dasar(nama_app, gambar_fungsi):
    # Buat folder jika belum ada
    path = f"aplikasi/{nama_app.lower()}"
    if not os.path.exists(path):
        os.makedirs(path)
    
    # Buat gambar hitam
    img = Image.new('RGBA', SIZE, BLACK)
    draw = ImageDraw.Draw(img)
    
    # Gambar bingkai neon
    draw.rectangle([10, 10, 190, 190], outline=NEON_GREEN, width=5)
    
    # Gambar simbol spesifik aplikasi
    gambar_fungsi(draw)
    
    # Simpan sebagai icon.png
    img.save(f"{path}/icon.png")
    print(f"✅ Ikon untuk {nama_app} berhasil dibuat!")

# --- Simbol-Simbol Aplikasi ---

def simbol_toko(d):
    d.rectangle([60, 60, 140, 140], outline=NEON_GREEN, width=3)
    d.line([100, 60, 100, 140], fill=NEON_GREEN, width=3)

def simbol_catatan(d):
    for y in range(60, 150, 30):
        d.line([50, y, 150, y], fill=NEON_GREEN, width=4)

def simbol_kalkulator(d):
    d.line([100, 60, 100, 140], fill=NEON_GREEN, width=5)
    d.line([60, 100, 140, 100], fill=NEON_GREEN, width=5)

def simbol_penjelajah(d):
    d.ellipse([60, 60, 140, 140], outline=NEON_GREEN, width=4)
    d.line([100, 60, 100, 140], fill=NEON_GREEN, width=2)
    d.line([60, 100, 140, 100], fill=NEON_GREEN, width=2)

def simbol_berkas(d):
    d.polygon([(50,70), (150,70), (150,140), (50,140)], outline=NEON_GREEN, width=4)
    d.line([50, 90, 150, 90], fill=NEON_GREEN, width=3)

# Eksekusi Pembuatan
buat_ikon_dasar("toko_simpul", simbol_toko)
buat_ikon_dasar("catatan", simbol_catatan)
buat_ikon_dasar("kalkulator", simbol_kalkulator)
buat_ikon_dasar("penjelajah", simbol_penjelajah)
buat_ikon_dasar("manajer-berkas", simbol_berkas)
