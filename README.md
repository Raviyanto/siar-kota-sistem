# Siar Kota OS (Sistem Utama)

Ini adalah "Otak" dari sistem operasi Siar Kota.
Berjalan di atas Debian 12 (Bookworm) tanpa Desktop Environment.

## Cara Instalasi Ulang

1. Instal Debian Minimal (Netinst).
2. Jangan pilih Desktop Environment, pilih "SSH Server" & "Standard Utilities".
3. Jalankan perintah instalasi dependensi:

```bash
sudo apt update
sudo apt install git python3-pip xorg openbox python3-pyqt6 python3-pyqt6.qtwebengine -y


startx /usr/bin/python3 /home/siar/Proyek_Siar/siar-kota-sistem/otak.py
```

