import mysql.connector
from mysql.connector import Error
import pandas as pd
from datetime import datetime

class DatabaseManager:
    def __init__(self, host="localhost", user="root", password="", database="telemetri_vault"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self, use_db=True):
        try:
            conn = mysql.connector.connect(
                host=self.host, user=self.user,
                password=self.password, database=self.database if use_db else None
            )
            return conn
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None

    def setup_database(self):
        conn = self.connect(use_db=False)
        if not conn: return False
        cursor = conn.cursor()
        try:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            cursor.execute(f"USE {self.database}")

            # Tabel Kelas & Mobil (Tetap sama)
            cursor.execute("CREATE TABLE IF NOT EXISTS tb_kelas_balap (id_kelas VARCHAR(50) PRIMARY KEY, nama_kelas VARCHAR(100))")
            cursor.execute("CREATE TABLE IF NOT EXISTS tb_mobil (id_mobil VARCHAR(50) PRIMARY KEY, id_kelas VARCHAR(50), pabrikan VARCHAR(100), model_kendaraan VARCHAR(100), FOREIGN KEY (id_kelas) REFERENCES tb_kelas_balap(id_kelas) ON DELETE CASCADE)")

            # BARU: Tabel Akun User
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tb_akun (
                    username VARCHAR(50) PRIMARY KEY,
                    password VARCHAR(255),
                    driver_nickname VARCHAR(100)
                )
            """)

            # PERUBAHAN: Relasi id_pembalap diganti jadi username
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tb_sesi_latihan (
                    id_sesi VARCHAR(100) PRIMARY KEY,
                    id_mobil VARCHAR(50),
                    username VARCHAR(50),
                    tipe_sesi VARCHAR(50),
                    waktu_unggah DATETIME,
                    FOREIGN KEY (id_mobil) REFERENCES tb_mobil(id_mobil) ON DELETE CASCADE,
                    FOREIGN KEY (username) REFERENCES tb_akun(username) ON DELETE CASCADE
                )
            """)

            # Tabel Log Big Data (Tetap sama)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tb_log_telemetri (
                    id_log BIGINT AUTO_INCREMENT PRIMARY KEY,
                    id_sesi VARCHAR(100),
                    lap_number INT, lap_distance FLOAT, speed_kmh FLOAT, gear INT, rpm INT,
                    throttle_input FLOAT, brake_input FLOAT, fuel_level FLOAT, oil_temp FLOAT, oil_pressure FLOAT,
                    FOREIGN KEY (id_sesi) REFERENCES tb_sesi_latihan(id_sesi) ON DELETE CASCADE
                )
            """)
            
            cursor.execute("INSERT IGNORE INTO tb_kelas_balap (id_kelas, nama_kelas) VALUES ('LMDh', 'Le Mans Daytona h')")
            cursor.execute("INSERT IGNORE INTO tb_mobil (id_mobil, id_kelas, pabrikan, model_kendaraan) VALUES ('LMDh-POR963', 'LMDh', 'Porsche', '963')")
            
            conn.commit()
            print("✅ Database versi terbaru (dengan sistem Akun) berhasil dibuat!")
            return True
        except Error as e:
            print(f"Error setup DB: {e}")
            return False
        finally:
            if conn.is_connected():
                cursor.close(); conn.close()

    def execute_query(self, query, params=None, fetch=False):
        conn = self.connect()
        if not conn: return None
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            if fetch: return cursor.fetchall()
            conn.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"Database Error: {e}")
            return None
        finally:
            if conn.is_connected():
                cursor.close(); conn.close()

    def insert_bulk_telemetry(self, id_sesi, df_cleaned):
        conn = self.connect()
        if not conn: return False
        cursor = conn.cursor()
        try:
            query = "INSERT INTO tb_log_telemetri (id_sesi, lap_number, lap_distance, speed_kmh, gear, rpm, throttle_input, brake_input, fuel_level, oil_temp, oil_pressure) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            data = [(id_sesi, row.get('lap_number', 0), row.get('lap_distance', 0.0), row.get('speed', 0.0), row.get('gear', 0), row.get('rpm', 0), row.get('throttle', 0.0), row.get('brake', 0.0), row.get('fuel_level', 0.0), row.get('oil_temp', 0.0), row.get('oil_pres', 0.0)) for _, row in df_cleaned.iterrows()]
            cursor.executemany(query, data)
            conn.commit()
            return True
        except Error as e:
            conn.rollback()
            return False
        finally:
            if conn.is_connected(): cursor.close(); conn.close()