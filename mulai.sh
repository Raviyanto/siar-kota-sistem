#!/bin/bash

# 1. Atur Resolusi Layar (Coba paksa ke 1280x720)
# Jika nanti masih kecil, kita akan ganti angkanya.
xrandr --output default --mode 1280x720 2>/dev/null || xrandr -s 1280x720

# 2. Matikan Screen Saver (Agar layar tidak mati sendiri)
xset s off
xset -dpms
xset s noblank

# 3. Jalankan Otak Utama
/usr/bin/python3 /home/siar/Proyek_Siar/siar-kota-sistem/otak.py