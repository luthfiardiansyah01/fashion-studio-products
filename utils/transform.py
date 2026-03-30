"""
Module untuk mentransformasi data produk yang telah di-scrape.
Melakukan pembersihan data dan konversi tipe data.
"""

import pandas as pd
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EXCHANGE_RATE = 16000  # 1 USD = 16000 IDR


def convert_price_to_idr(price_str: str) -> float:
    """
    Mengkonversi harga dari USD ke IDR.
    """
    try:
        if price_str is None:
            return None
            
        # Hapus tanda $ dan whitespace
        cleaned = str(price_str).replace('$', '').strip()
        
        # Konversi ke float
        price_usd = float(cleaned)
        
        # Konversi ke IDR
        price_idr = price_usd * EXCHANGE_RATE
        return price_idr
    except (ValueError, TypeError, AttributeError) as e:
        logger.warning(f"Error converting price '{price_str}': {e}")
        return None


def clean_rating(rating_str: str) -> float:
    """
    Membersihkan string rating dan mengkonversi ke float.
    """
    try:
        if rating_str is None:
            return None
            
        if 'Invalid Rating' in str(rating_str) or 'Not Rated' in str(rating_str):
            return None
        
        # Ekstrak nilai numerik dari string seperti "Rating: ⭐ 4.8 / 5"
        match = re.search(r'(\d+\.?\d*)', str(rating_str))
        if match:
            return float(match.group(1))
        return None
    except (ValueError, TypeError, AttributeError) as e:
        logger.warning(f"Error cleaning rating '{rating_str}': {e}")
        return None


def clean_colors(colors_str: str) -> int:
    """
    Membersihkan string colors dan mengekstrak angka saja.
    """
    try:
        if colors_str is None:
            return None
        
        # Ekstrak nilai numerik dari string seperti "3 Colors"
        match = re.search(r'(\d+)', str(colors_str))
        if match:
            return int(match.group(1))
        return None
    except (ValueError, TypeError, AttributeError) as e:
        logger.warning(f"Error cleaning colors '{colors_str}': {e}")
        return None


def clean_size(size_str: str) -> str:
    """
    Membersihkan string size dengan menghapus prefix 'Size: '.
    """
    try:
        if size_str is None:
            return None
        
        # Hapus prefix "Size: " termasuk leading whitespace
        cleaned = re.sub(r'^\s*Size:\s*', '', str(size_str))
        return cleaned.strip() if cleaned.strip() else None
    except (TypeError, AttributeError) as e:
        logger.warning(f"Error cleaning size '{size_str}': {e}")
        return None


def clean_gender(gender_str: str) -> str:
    """
    Membersihkan string gender dengan menghapus prefix 'Gender: '.
    """
    try:
        if gender_str is None:
            return None
        
        # Hapus prefix "Gender: " termasuk leading whitespace
        cleaned = re.sub(r'^\s*Gender:\s*', '', str(gender_str))
        return cleaned.strip() if cleaned.strip() else None
    except (TypeError, AttributeError) as e:
        logger.warning(f"Error cleaning gender '{gender_str}': {e}")
        return None


def remove_invalid_products(df: pd.DataFrame) -> pd.DataFrame:
    """
    Menghapus produk dengan title 'Unknown Product'.
    """
    try:
        initial_count = len(df)
        df_clean = df[df['title'] != 'Unknown Product']
        removed_count = initial_count - len(df_clean)
        if removed_count > 0:
            logger.info(f"Removed {removed_count} invalid products")
        return df_clean
    except Exception as e:
        logger.error(f"Error removing invalid products: {e}")
        raise


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Menghapus data duplikat dari DataFrame.
    """
    try:
        initial_count = len(df)
        df_clean = df.drop_duplicates()
        duplicates_removed = initial_count - len(df_clean)
        if duplicates_removed > 0:
            logger.info(f"Removed {duplicates_removed} duplicate rows")
        return df_clean
    except Exception as e:
        logger.error(f"Error removing duplicates: {e}")
        raise


def remove_nulls(df: pd.DataFrame) -> pd.DataFrame:
    """
    Menghapus baris dengan nilai null dari DataFrame.
    """
    try:
        initial_count = len(df)
        df_clean = df.dropna()
        nulls_removed = initial_count - len(df_clean)
        if nulls_removed > 0:
            logger.info(f"Removed {nulls_removed} rows with null values")
        return df_clean
    except Exception as e:
        logger.error(f"Error removing nulls: {e}")
        raise


def convert_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mengkonversi tipe data setiap kolom sesuai dengan yang diharapkan.
    Menggunakan astype(object) untuk string agar kompatibel dengan semua versi Pandas.
    """
    try:
        df['price'] = df['price'].astype(float)
        df['rating'] = df['rating'].astype(float)
        df['colors'] = df['colors'].astype(int)
        # Menggunakan 'object' secara eksplisit untuk menghindari StringDtype di Pandas 2.x
        df['size'] = df['size'].astype(object)
        df['gender'] = df['gender'].astype(object)
        df['title'] = df['title'].astype(object)
        return df
    except (ValueError, TypeError) as e:
        logger.error(f"Error converting data types: {e}")
        raise
    except KeyError as e:
        logger.error(f"Missing column in data types conversion: {e}")
        raise


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fungsi utama untuk mentransformasi data yang telah di-scrape.
    """
    try:
        if df.empty:
            raise ValueError("Input DataFrame is empty")
        
        # Verifikasi kolom yang diperlukan
        required_columns = ['title', 'price', 'rating', 'colors', 'size', 'gender', 'timestamp']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise KeyError(f"Missing required columns: {missing_columns}")
        
        # Buat copy untuk menghindari SettingWithCopyWarning
        df_clean = df.copy()
        
        # Hapus produk invalid ('Unknown Product')
        df_clean = remove_invalid_products(df_clean)
        
        # Konversi Price ke IDR
        df_clean['price'] = df_clean['price'].apply(convert_price_to_idr)
        
        # Bersihkan Rating
        df_clean['rating'] = df_clean['rating'].apply(clean_rating)
        
        # Bersihkan Colors
        df_clean['colors'] = df_clean['colors'].apply(clean_colors)
        
        # Bersihkan Size
        df_clean['size'] = df_clean['size'].apply(clean_size)
        
        # Bersihkan Gender
        df_clean['gender'] = df_clean['gender'].apply(clean_gender)
        
        # Hapus duplikat
        df_clean = remove_duplicates(df_clean)
        
        # Hapus baris dengan nilai null
        df_clean = remove_nulls(df_clean)
        
        # Konversi tipe data
        df_clean = convert_data_types(df_clean)
        
        # Reset index
        df_clean = df_clean.reset_index(drop=True)
        
        logger.info(f"Transformed data: {len(df_clean)} rows")
        return df_clean
        
    except ValueError as e:
        logger.error(f"Value error in transform_data: {e}")
        raise
    except KeyError as e:
        logger.error(f"Key error in transform_data: {e}")
        raise
    except Exception as e:
        logger.error(f"Error in transform_data: {e}")
        raise