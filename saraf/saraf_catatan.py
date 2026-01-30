import os
from PyQt6.QtCore import QObject, pyqtSlot

class CatatanSaraf(QObject):
    def __init__(self):
        super().__init__()
        # Menentukan folder penyimpanan dokumen
        self.folder_simpan = os.path.expanduser("~/Dokumen/Siar_Catatan")
        if not os.path.exists(self.folder_simpan):
            os.makedirs(self.folder_simpan)

    @pyqtSlot(str, str, result=str)
    def simpan_ke_berkas(self, nama_file, isi_teks):
        try:
            # Membersihkan nama file dan menambahkan ekstensi .txt
            nama_bersih = nama_file.strip().replace(" ", "_")
            if not nama_bersih.endswith(".txt"):
                nama_bersih += ".txt"
            
            path_lengkap = os.path.join(self.folder_simpan, nama_bersih)
            with open(path_lengkap, "w", encoding="utf-8") as f:
                f.write(isi_teks)
            
            return f"✅ Berhasil: {nama_bersih} disimpan di Dokumen"
        except Exception as e:
            return f"❌ Error: {str(e)}"
