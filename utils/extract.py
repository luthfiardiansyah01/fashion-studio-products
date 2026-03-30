"""
Module untuk mengekstrak data produk dari website Fashion Studio.
Mengambil data dari halaman 1 hingga 50.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "https://fashion-studio.dicoding.dev/"


def scrape_page(page_number: int) -> list:
    """
    Mengekstrak data produk dari satu halaman website.
    
    Args:
        page_number: Nomor halaman yang akan di-scrape
        
    Returns:
        List of dictionaries berisi data produk
        
    Raises:
        requests.exceptions.RequestException: Jika halaman tidak dapat diakses
        Exception: Untuk error yang tidak terduga
    """
    try:
        # Perbaikan format URL pagination (halaman 1 = root, halaman 2 = /page2)
        if page_number == 1:
            url = BASE_URL
        else:
            url = f"{BASE_URL}page{page_number}"
            
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        products = []
        
        # Perbaikan class container: menggunakan 'collection-card'
        product_cards = soup.find_all('div', class_='collection-card')
        
        for card in product_cards:
            try:
                # Ekstrak title
                title_elem = card.find('h3', class_='product-title')
                title = title_elem.text.strip() if title_elem else None
                
                # Ekstrak price (bisa berupa <span class="price"> atau <p class="price">)
                price_elem = card.find('span', class_='price') or card.find('p', class_='price')
                price = price_elem.text.strip() if price_elem else None
                
                # Inisialisasi variabel lainnya
                rating = None
                colors = None
                size = None
                gender = None
                
                # Perbaikan: Ekstrak Rating, Colors, Size, Gender dari tag <p> generik
                detail_paragraphs = card.find_all('p')
                for p in detail_paragraphs:
                    text = p.get_text(strip=True)
                    
                    if text.startswith('Rating:'):
                        rating = text
                    elif 'Colors' in text:
                        colors = text
                    elif text.startswith('Size:'):
                        size = text
                    elif text.startswith('Gender:'):
                        gender = text
                
                product = {
                    'title': title,
                    'price': price,
                    'rating': rating,
                    'colors': colors,
                    'size': size,
                    'gender': gender,
                    'timestamp': datetime.now().isoformat()
                }
                products.append(product)
                
            except AttributeError as e:
                logger.warning(f"Error parsing product card: {e}")
                continue
            except Exception as e:
                logger.warning(f"Unexpected error parsing product: {e}")
                continue
        
        return products
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout error while fetching page {page_number}")
        raise
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error while fetching page {page_number}")
        raise
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error while fetching page {page_number}: {e}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error while fetching page {page_number}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error on page {page_number}: {e}")
        raise


def scrape_all_pages(start_page: int = 1, end_page: int = 50) -> pd.DataFrame:
    """
    Mengekstrak data produk dari semua halaman website.
    
    Args:
        start_page: Nomor halaman awal (default: 1)
        end_page: Nomor halaman akhir (default: 50)
        
    Returns:
        DataFrame berisi semua data produk yang di-scrape
        
    Raises:
        ValueError: Jika tidak ada data yang berhasil di-scrape
        Exception: Untuk error lainnya
    """
    try:
        all_products = []
        
        for page in range(start_page, end_page + 1):
            try:
                products = scrape_page(page)
                all_products.extend(products)
                logger.info(f"Scraped page {page}, got {len(products)} products")
                time.sleep(0.5)  # Rate limiting untuk menghormati server
            except requests.exceptions.RequestException as e:
                logger.warning(f"Skipping page {page} due to request error: {e}")
                continue
            except Exception as e:
                logger.warning(f"Skipping page {page} due to error: {e}")
                continue
        
        if not all_products:
            raise ValueError("No products were scraped from any page")
        
        df = pd.DataFrame(all_products)
        logger.info(f"Total products scraped: {len(df)}")
        return df
        
    except ValueError as e:
        logger.error(f"Value error in scrape_all_pages: {e}")
        raise
    except Exception as e:
        logger.error(f"Error in scrape_all_pages: {e}")
        raise