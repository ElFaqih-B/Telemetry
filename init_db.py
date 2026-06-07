from models.db_manager import DatabaseManager

if __name__ == "__main__":
    print("Membentuk Arsitektur Data Vault Telemetri...")
    db = DatabaseManager()
    
    # Fungsi ini akan mengeksekusi semua instruksi DDL (Data Definition Language)
    sukses = db.setup_database()
    
    if sukses:
        print("Sistem siap digunakan! Silakan jalankan: streamlit run main.py")
    else:
        print("Gagal membuat database. Cek apakah MySQL Server/XAMPP sudah menyala.")