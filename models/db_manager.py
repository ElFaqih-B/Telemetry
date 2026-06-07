import mysql.connector
from mysql.connector import Error
import pandas as pd
from datetime import datetime

class DatabaseManager:
    def __init__(self, host="localhost", user="root", password="", database="performa_mobil"):
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

            # Kelas Balap
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS kelas_balap (
                    id_kelas VARCHAR(10) PRIMARY KEY,
                    nama_kelas VARCHAR(100)
                )
            """)

            # Mobil
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mobil (
                    id_mobil VARCHAR(50) PRIMARY KEY,
                    id_kelas VARCHAR(10),
                    pabrikan VARCHAR(50),
                    model_kendaraan VARCHAR(100),
                    FOREIGN KEY (id_kelas) REFERENCES kelas_balap(id_kelas) ON DELETE CASCADE
                )
            """)

            # Pembalap
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pembalap (
                    id_pembalap VARCHAR(15) PRIMARY KEY,
                    nama_pembalap VARCHAR(100)
                )
            """)

            # Pengguna (Akun)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pengguna (
                    id_user INT AUTO_INCREMENT PRIMARY KEY,
                    nama_lengkap VARCHAR(100),
                    email VARCHAR(255) UNIQUE,
                    password_hash VARCHAR(255),
                    role_pengguna VARCHAR(50)
                )
            """)

            # Sesi Latihan
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sesi_latihan (
                    id_sesi VARCHAR(50) PRIMARY KEY,
                    id_mobil VARCHAR(50),
                    id_pembalap VARCHAR(15),
                    id_user INT,
                    tipe_sesi VARCHAR(50),
                    waktu_unggahan DATETIME,
                    FOREIGN KEY (id_mobil) REFERENCES mobil(id_mobil) ON DELETE CASCADE,
                    FOREIGN KEY (id_pembalap) REFERENCES pembalap(id_pembalap) ON DELETE CASCADE,
                    FOREIGN KEY (id_user) REFERENCES pengguna(id_user) ON DELETE CASCADE
                )
            """)

            # Log Telemetri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS log_telemetri (
                    id_log BIGINT AUTO_INCREMENT PRIMARY KEY,
                    id_sesi VARCHAR(50),
                    lap_number INT, lap_distance FLOAT, speed_kmh FLOAT, gear INT, rpm INT,
                    throttle_input FLOAT, brake_input FLOAT, fuel_level FLOAT, oil_temp FLOAT, oil_pressure FLOAT,
                    FOREIGN KEY (id_sesi) REFERENCES sesi_latihan(id_sesi) ON DELETE CASCADE
                )
            """)
            
            # Initial Data Seed
            cursor.execute("INSERT IGNORE INTO kelas_balap (id_kelas, nama_kelas) VALUES ('LMDh', 'Le Mans Daytona h'), ('LMP2', 'Le Mans Prototype 2'), ('LMGT3', 'Le Mans GT3')")
            cursor.execute("INSERT IGNORE INTO mobil (id_mobil, id_kelas, pabrikan, model_kendaraan) VALUES ('LMDh-POR963', 'LMDh', 'Porsche', '963'), ('LMP2-ORE07', 'LMP2', 'Oreca', '07'), ('LMGT3-FER911', 'LMGT3', 'Ferrari', '296 GT3')")
            
            conn.commit()
            print("✅ Database performa_mobil siap digunakan!")
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
            query = """INSERT INTO log_telemetri 
                       (id_sesi, lap_number, lap_distance, speed_kmh, gear, rpm, throttle_input, brake_input, fuel_level, oil_temp, oil_pressure) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            data = [(id_sesi, row.get('lap_number', 1), row.get('lap_distance', 0.0), row.get('speed', 0.0), 
                     row.get('gear', 0), row.get('rpm', 0), row.get('throttle', 0.0), row.get('brake', 0.0), 
                     row.get('fuel_level', 0.0), row.get('oil_temp', 0.0), row.get('oil_pres', 0.0)) for _, row in df_cleaned.iterrows()]
            cursor.executemany(query, data)
            conn.commit()
            return True
        except Error as e:
            conn.rollback()
            print(f"Bulk Insert Error: {e}")
            return False
        finally:
            if conn.is_connected(): cursor.close(); conn.close()