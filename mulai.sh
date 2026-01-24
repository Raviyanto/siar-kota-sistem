#!/bin/bash

# === 1. AKTIFKAN AGEN RAHASIA (PENTING!) ===
# VBoxClient bertugas mendengarkan perubahan ukuran layar dari Windows.
# Tanpa ini, fitur Auto-Resize tidak akan jalan.
/usr/bin/VBoxClient-all 2>/dev/null || VBoxClient-all
# (Cadangan jika perintah all tidak ada, kita panggil satu per satu)
VBoxClient --clipboard 2>/dev/null
VBoxClient --draganddrop 2>/dev/null
VBoxClient --display 2>/dev/null
VBoxClient --seamless 2>/dev/null
VBoxClient --checkhostversion 2>/dev/null

# Beri waktu agen untuk melapor
sleep 1

# === 2. PAKSA RESOLUSI AWAL ===
# Coba trigger auto-resize sekali
xrandr --auto 2>/dev/null

# === 3. SETTING LAYAR (ANTI MATI) ===
xset s off
xset -dpms
xset s noblank

# === 4. JALANKAN WINDOW MANAGER & APLIKASI ===
# Kita jalankan Openbox di background supaya manajemen jendela lebih stabil
openbox &

# Jalankan Otak Python
# "exec" berarti script ini selesai dan digantikan sepenuhnya oleh Python
exec /usr/bin/python3 /home/siar/Proyek_Siar/siar-kota-sistem/otak.py