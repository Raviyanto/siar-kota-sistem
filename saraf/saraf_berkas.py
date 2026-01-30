import os
import shutil
from PyQt6.QtCore import QObject, pyqtSlot

class BerkasSaraf(QObject):
    def __init__(self):
        super().__init__()
        self.home_path = os.path.expanduser("~")

    @pyqtSlot(str, result=list)
    def telusuri_folder(self, path_relatif=""):
        try:
            target_path = os.path.join(self.home_path, path_relatif)
            item_list = []
            for item in os.listdir(target_path):
                full_item_path = os.path.join(target_path, item)
                item_list.append({
                    "nama": item,
                    "tipe": "folder" if os.path.isdir(full_item_path) else "berkas",
                    "path_relatif": os.path.relpath(full_item_path, self.home_path)
                })
            return item_list
        except Exception as e:
            return [{"nama": f"Error: {str(e)}", "tipe": "error", "path_relatif": ""}]

    @pyqtSlot(str, result=str)
    def baca_isi_berkas(self, path_relatif):
        try:
            full_path = os.path.join(self.home_path, path_relatif)
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Gagal membaca: {str(e)}"

    @pyqtSlot(str, result=bool)
    def hapus_item(self, path_relatif):
        try:
            full_path = os.path.join(self.home_path, path_relatif)
            if os.path.isdir(full_path):
                shutil.rmtree(full_path)
            else:
                os.remove(full_path)
            return True
        except:
            return False

    @pyqtSlot(str, str, result=bool)
    def ganti_nama(self, path_relatif, nama_baru):
        try:
            old_path = os.path.join(self.home_path, path_relatif)
            new_path = os.path.join(os.path.dirname(old_path), nama_baru)
            os.rename(old_path, new_path)
            return True
        except:
            return False
