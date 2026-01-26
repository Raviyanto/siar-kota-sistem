#!/bin/bash

# === 1. AKTIFKAN AGEN RAHASIA (SILENT MODE) ===
# Kita buang semua output (> /dev/null 2>&1) agar tidak mencetak teks di layar.
/usr/bin/VBoxClient-all > /dev/null 2>&1 || VBoxClient-all > /dev/null 2>&1

# Cadangan panggil satu per satu tanpa suara
VBoxClient --clipboard > /dev/null 2>&1
VBoxClient --draganddrop > /dev/null 2>&1
VBoxClient --display > /dev/null 2>&1
VBoxClient --seamless > /dev/null 2>&1
VBoxClient --checkhostversion > /dev/null 2>&1

# Beri waktu agen untuk melapor tanpa interupsi visual
sleep 1

# === 2. PAKSA RESOLUSI AWAL ===
xrandr --auto > /dev/null 2>&1

# === 3. SETTING LAYAR (ANTI MATI) ===
xset s off > /dev/null 2>&1
xset -dpms > /dev/null 2>&1
xset s noblank > /dev/null 2>&1

# === 4. JALANKAN WINDOW MANAGER & APLIKASI ===
# Jalankan Openbox di background dan buang log-nya (agar log di foto hilang)
openbox > /dev/null 2>&1 &

# Tunggu sebentar agar Openbox siap sebelum memanggil GUI
sleep 0.5

# === 5. JALANKAN OTAK PYTHON (FINAL) ===
# Pengalihan output di sini sangat krusial untuk menghilangkan log di monitor
exec /usr/bin/python3 /home/siar/Proyek_Siar/siar-kota-sistem/otak.py > /dev/null 2>&1