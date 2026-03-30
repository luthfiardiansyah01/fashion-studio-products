"""
Module untuk memuat data yang telah ditransformasi ke berbagai repositori data.
Mendukung penyimpanan ke CSV, Google Sheets, dan PostgreSQL.
"""

import pandas as pd
import os
import logging
from dotenv import load_dotenv

# Coba import library opsional
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

try:
    import psycopg2
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

CSV_FILE_PATH = "products.csv"
GOOGLE_SHEETS_CREDENTIALS_PATH = "google-sheets-api.json"
GOOGLE_SHEET_NAME = "Fashion Studio Products"
TABLE_NAME = "fashion_products"


def save_to_csv(df: pd.DataFrame, file_path: str = CSV_FILE_PATH) -> bool:
    """
    Menyimpan DataFrame ke file CSV.
    
    Args:
        df: DataFrame yang akan disimpan
        file_path: Path untuk menyimpan file CSV
        
    Returns:
        True jika berhasil, False jika gagal
        
    Raises:
        ValueError: Jika DataFrame kosong
        PermissionError: Jika tidak memiliki akses tulis
        Exception: Untuk error lainnya
    """
    try:
        if df.empty:
            raise ValueError("DataFrame is empty, cannot save to CSV")
        
        # Pastikan direktori ada
        os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else '.', exist_ok=True)
        
        df.to_csv(file_path, index=False)
        logger.info(f"Successfully saved {len(df)} rows to {file_path}")
        return True
        
    except ValueError as e:
        logger.error(f"Value error saving to CSV: {e}")
        raise
    except PermissionError:
        logger.error(f"Permission denied when saving to {file_path}")
        raise
    except OSError as e:
        logger.error(f"OS error saving to CSV: {e}")
        raise
    except Exception as e:
        logger.error(f"Error saving to CSV: {e}")
        raise


def save_to_google_sheets(df: pd.DataFrame, 
                          credentials_path: str = GOOGLE_SHEETS_CREDENTIALS_PATH,
                          sheet_name: str = GOOGLE_SHEET_NAME) -> bool:
    """
    Menyimpan DataFrame ke Google Sheets.
    """
    try:
        if not GSPREAD_AVAILABLE:
            raise ImportError("gspread library is not installed")
            
        if df.empty:
            raise ValueError("DataFrame is empty, cannot save to Google Sheets")
        
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(f"Google Sheets credentials file not found: {credentials_path}")
        
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = Credentials.from_service_account_file(credentials_path, scopes=scopes)
        client = gspread.authorize(creds)
        
        # Coba buka spreadsheet yang sudah ada
        try:
            spreadsheet = client.open(sheet_name)
        except gspread.SpreadsheetNotFound:
            # Jika tidak ada, buat baru (hanya sekali dalam seumur hidup project ini)
            spreadsheet = client.create(sheet_name)
            spreadsheet.share('', perm_type='anyone', role='editor')
        
        # Gunakan worksheet pertama
        worksheet = spreadsheet.sheet1
        
        # Hanya resize kolom jika ini pertama kali atau ukurannya berbeda
        # Lalu clear dan replace seluruh datanya (lebih aman daripada append)
        worksheet.clear()
        
        # Konversi DataFrame ke list of lists
        data_to_upload = [df.columns.values.tolist()] + df.values.tolist()
        worksheet.update(data_to_upload, value_input_option='RAW')
        
        logger.info(f"Successfully saved {len(df)} rows to Google Sheets: {sheet_name}")
        logger.info(f"Google Sheets URL: {spreadsheet.url}")
        return True
        
    except ImportError as e:
        logger.error(f"Import error for Google Sheets: {e}")
        raise
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise
    except gspread.exceptions.APIError as e:
        logger.error(f"Google Sheets API error: {e}")
        raise
    except gspread.exceptions.GSpreadException as e:
        logger.error(f"GSpread error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error saving to Google Sheets: {e}")
        raise


def save_to_postgresql(df: pd.DataFrame, table_name: str = TABLE_NAME) -> bool:
    """
    Menyimpan DataFrame ke database PostgreSQL.
    
    Args:
        df: DataFrame yang akan disimpan
        table_name: Nama tabel untuk menyimpan data
        
    Returns:
        True jika berhasil, False jika gagal
        
    Raises:
        ImportError: Jika psycopg2 tidak terinstal
        ValueError: Jika DataFrame kosong
        psycopg2.OperationalError: Jika koneksi gagal
        Exception: Untuk error lainnya
    """
    try:
        if not PSYCOPG2_AVAILABLE:
            raise ImportError("psycopg2 library is not installed")
            
        if df.empty:
            raise ValueError("DataFrame is empty, cannot save to PostgreSQL")
        
        # Ambil parameter koneksi dari environment variables
        db_host = os.getenv('DB_HOST', 'aws-1-ap-southeast-1.pooler.supabase.com')
        db_port = os.getenv('DB_PORT', '6543')
        db_name = os.getenv('DB_NAME', 'postgres')
        db_user = os.getenv('DB_USER', 'postgres.xkecqmpovaknnqxttxed')
        db_password = os.getenv('DB_PASSWORD', 'kaWyxyb9xHfP9nZQ')
        
        # Koneksi ke database
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_password,
            sslmode='require'
        )
        
        cursor = conn.cursor()
        
        # Hapus tabel jika ada dan buat tabel baru
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        
        create_table_query = f"""
        CREATE TABLE {table_name} (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255),
            price FLOAT,
            rating FLOAT,
            colors INTEGER,
            size VARCHAR(100),
            gender VARCHAR(50),
            timestamp VARCHAR(50)
        )
        """
        cursor.execute(create_table_query)
        
        # Insert data
        insert_query = f"""
        INSERT INTO {table_name} (title, price, rating, colors, size, gender, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        for _, row in df.iterrows():
            cursor.execute(insert_query, (
                row['title'],
                row['price'],
                row['rating'],
                row['colors'],
                row['size'],
                row['gender'],
                row['timestamp']
            ))
        
        conn.commit()
        
        # Verifikasi jumlah data
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        logger.info(f"Successfully saved {count} rows to PostgreSQL table: {table_name}")
        return True
        
    except ImportError as e:
        logger.error(f"Import error for PostgreSQL: {e}")
        raise
    except psycopg2.OperationalError as e:
        logger.error(f"PostgreSQL connection error: {e}")
        raise
    except psycopg2.ProgrammingError as e:
        logger.error(f"PostgreSQL programming error: {e}")
        raise
    except psycopg2.Error as e:
        logger.error(f"PostgreSQL error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error saving to PostgreSQL: {e}")
        raise


def load_data(df: pd.DataFrame, 
              save_csv: bool = True,
              save_sheets: bool = False,
              save_postgres: bool = False) -> dict:
    """
    Fungsi utama untuk memuat data ke repositori yang ditentukan.
    
    Args:
        df: DataFrame yang akan disimpan
        save_csv: Apakah menyimpan ke CSV
        save_sheets: Apakah menyimpan ke Google Sheets
        save_postgres: Apakah menyimpan ke PostgreSQL
        
    Returns:
        Dictionary dengan status setiap operasi penyimpanan
    """
    results = {
        'csv': None,
        'google_sheets': None,
        'postgresql': None
    }
    
    try:
        if save_csv:
            results['csv'] = save_to_csv(df)
        
        if save_sheets:
            try:
                results['google_sheets'] = save_to_google_sheets(df)
            except Exception as e:
                logger.warning(f"Failed to save to Google Sheets: {e}")
                results['google_sheets'] = False
        
        if save_postgres:
            try:
                results['postgresql'] = save_to_postgresql(df)
            except Exception as e:
                logger.warning(f"Failed to save to PostgreSQL: {e}")
                results['postgresql'] = False
        
        return results
        
    except Exception as e:
        logger.error(f"Error in load_data: {e}")
        raise