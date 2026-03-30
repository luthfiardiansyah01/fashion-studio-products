"""
Unit tests untuk module extract.py
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from datetime import datetime
from utils.extract import scrape_page, scrape_all_pages, BASE_URL
import requests


# Mock HTML Template sesuai dengan struktur asli website Fashion Studio
MOCK_HTML_SINGLE = '''
<html><body>
    <div class="collection-card">
        <h3 class="product-title">Test T-Shirt</h3>
        <span class="price">$25.00</span>
        <p style="font-size: 14px; color: #777;">Rating: ⭐ 4.8 / 5</p>
        <p style="font-size: 14px; color: #777;">3 Colors</p>
        <p style="font-size: 14px; color: #777;">Size: M, L, XL</p>
        <p style="font-size: 14px; color: #777;">Gender: Men</p>
    </div>
</body></html>
'''

MOCK_HTML_MULTIPLE = '''
<html><body>
    <div class="collection-card">
        <h3 class="product-title">Product 1</h3>
        <span class="price">$10.00</span>
        <p style="font-size: 14px; color: #777;">Rating: ⭐ 4.5 / 5</p>
        <p style="font-size: 14px; color: #777;">2 Colors</p>
        <p style="font-size: 14px; color: #777;">Size: S, M</p>
        <p style="font-size: 14px; color: #777;">Gender: Women</p>
    </div>
    <div class="collection-card">
        <h3 class="product-title">Product 2</h3>
        <span class="price">$20.00</span>
        <p style="font-size: 14px; color: #777;">Rating: ⭐ 4.0 / 5</p>
        <p style="font-size: 14px; color: #777;">4 Colors</p>
        <p style="font-size: 14px; color: #777;">Size: L, XL</p>
        <p style="font-size: 14px; color: #777;">Gender: Men</p>
    </div>
    <div class="collection-card">
        <h3 class="product-title">Product 3</h3>
        <span class="price">$30.00</span>
        <p style="font-size: 14px; color: #777;">Rating: ⭐ 5.0 / 5</p>
        <p style="font-size: 14px; color: #777;">1 Colors</p>
        <p style="font-size: 14px; color: #777;">Size: M</p>
        <p style="font-size: 14px; color: #777;">Gender: Unisex</p>
    </div>
</body></html>
'''

MOCK_HTML_UNKNOWN = '''
<html><body>
    <div class="collection-card">
        <h3 class="product-title">Unknown Product</h3>
        <span class="price">$0.00</span>
        <p style="font-size: 14px; color: #777;">Rating: ⭐ Invalid Rating / 5</p>
        <p style="font-size: 14px; color: #777;">0 Colors</p>
        <p style="font-size: 14px; color: #777;">Size: </p>
        <p style="font-size: 14px; color: #777;">Gender: </p>
    </div>
</body></html>
'''

MOCK_HTML_PARTIAL = '''
<html><body>
    <div class="collection-card">
        <h3 class="product-title">Partial Product</h3>
        <span class="price">$15.00</span>
    </div>
</body></html>
'''

MOCK_HTML_EMPTY = '<html><body></body></html>'


class TestScrapePage:
    """Tests untuk fungsi scrape_page"""
    
    @patch('utils.extract.requests.get')
    def test_scrape_page_success_single_product(self, mock_get):
        """Test scraping halaman dengan satu produk berhasil"""
        mock_response = MagicMock()
        mock_response.text = MOCK_HTML_SINGLE
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        result = scrape_page(1)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['title'] == 'Test T-Shirt'
        assert result[0]['price'] == '$25.00'
        assert result[0]['rating'] == 'Rating: ⭐ 4.8 / 5'
        assert result[0]['colors'] == '3 Colors'
        assert result[0]['size'] == 'Size: M, L, XL'
        assert result[0]['gender'] == 'Gender: Men'
        assert 'timestamp' in result[0]
    
    @patch('utils.extract.requests.get')
    def test_scrape_page_multiple_products(self, mock_get):
        """Test scraping halaman dengan beberapa produk"""
        mock_response = MagicMock()
        mock_response.text = MOCK_HTML_MULTIPLE
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        result = scrape_page(1)
        
        assert len(result) == 3
        assert result[0]['title'] == 'Product 1'
        assert result[1]['title'] == 'Product 2'
        assert result[2]['title'] == 'Product 3'
    
    @patch('utils.extract.requests.get')
    def test_scrape_page_empty_page(self, mock_get):
        """Test scraping halaman tanpa produk"""
        mock_response = MagicMock()
        mock_response.text = MOCK_HTML_EMPTY
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        result = scrape_page(1)
        
        assert isinstance(result, list)
        assert len(result) == 0
    
    @patch('utils.extract.requests.get')
    def test_scrape_page_with_unknown_product(self, mock_get):
        """Test scraping halaman dengan Unknown Product"""
        mock_response = MagicMock()
        mock_response.text = MOCK_HTML_UNKNOWN
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        result = scrape_page(1)
        
        assert len(result) == 1
        assert result[0]['title'] == 'Unknown Product'
    
    @patch('utils.extract.requests.get')
    def test_scrape_page_connection_error(self, mock_get):
        """Test handling connection error"""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        with pytest.raises(requests.exceptions.ConnectionError):
            scrape_page(1)
    
    @patch('utils.extract.requests.get')
    def test_scrape_page_timeout_error(self, mock_get):
        """Test handling timeout error"""
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
        
        with pytest.raises(requests.exceptions.Timeout):
            scrape_page(1)
    
    @patch('utils.extract.requests.get')
    def test_scrape_page_http_error(self, mock_get):
        """Test handling HTTP error"""
        mock_get.side_effect = requests.exceptions.HTTPError("404 Not Found")
        
        with pytest.raises(requests.exceptions.HTTPError):
            scrape_page(1)
    
    @patch('utils.extract.requests.get')
    def test_scrape_page_request_exception(self, mock_get):
        """Test handling generic request exception"""
        mock_get.side_effect = requests.exceptions.RequestException("Request failed")
        
        with pytest.raises(requests.exceptions.RequestException):
            scrape_page(1)
    
    @patch('utils.extract.requests.get')
    def test_scrape_page_correct_url_format(self, mock_get):
        """Test bahwa URL yang benar digunakan sesuai format website (/page2)"""
        mock_response = MagicMock()
        mock_response.text = MOCK_HTML_EMPTY
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        scrape_page(5)
        
        # Cek apakah URL yang dipanggil sesuai format /page{number}
        mock_get.assert_called_once_with(f"{BASE_URL}page5", timeout=30)
    
    @patch('utils.extract.requests.get')
    def test_scrape_page_missing_elements(self, mock_get):
        """Test scraping dengan beberapa elemen yang hilang"""
        mock_response = MagicMock()
        mock_response.text = MOCK_HTML_PARTIAL
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        result = scrape_page(1)
        
        assert len(result) == 1
        assert result[0]['title'] == 'Partial Product'
        assert result[0]['price'] == '$15.00'
        assert result[0]['rating'] is None
        assert result[0]['colors'] is None
        assert result[0]['size'] is None
        assert result[0]['gender'] is None


class TestScrapeAllPages:
    """Tests untuk fungsi scrape_all_pages"""
    
    @patch('utils.extract.scrape_page')
    def test_scrape_all_pages_success(self, mock_scrape):
        """Test scraping semua halaman berhasil"""
        mock_scrape.return_value = [
            {
                'title': 'Test Product',
                'price': '$25.00',
                'rating': 'Rating: ⭐ 4.5 / 5',
                'colors': '3 Colors',
                'size': 'Size: M, L',
                'gender': 'Gender: Men',
                'timestamp': datetime.now().isoformat()
            }
        ]
        
        result = scrape_all_pages(start_page=1, end_page=3)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert mock_scrape.call_count == 3
    
    @patch('utils.extract.scrape_page')
    def test_scrape_all_pages_with_partial_errors(self, mock_scrape):
        """Test scraping ketika beberapa halaman gagal"""
        def side_effect(page):
            if page == 2:
                raise requests.exceptions.ConnectionError("Page error")
            return [{
                'title': f'Product {page}',
                'price': '$10.00',
                'rating': 'Rating: ⭐ 4.0 / 5',
                'colors': '2 Colors',
                'size': 'Size: M',
                'gender': 'Gender: Women',
                'timestamp': datetime.now().isoformat()
            }]
        
        mock_scrape.side_effect = side_effect
        
        result = scrape_all_pages(start_page=1, end_page=3)
        
        assert len(result) == 2
        assert mock_scrape.call_count == 3
    
    @patch('utils.extract.scrape_page')
    def test_scrape_all_pages_no_data(self, mock_scrape):
        """Test scraping ketika tidak ada data yang dikembalikan"""
        mock_scrape.return_value = []
        
        with pytest.raises(ValueError, match="No products were scraped"):
            scrape_all_pages(start_page=1, end_page=3)
    
    @patch('utils.extract.scrape_page')
    def test_scrape_all_pages_all_errors(self, mock_scrape):
        """Test scraping ketika semua halaman gagal"""
        mock_scrape.side_effect = requests.exceptions.ConnectionError("All pages failed")
        
        with pytest.raises(ValueError, match="No products were scraped"):
            scrape_all_pages(start_page=1, end_page=3)
    
    @patch('utils.extract.scrape_page')
    def test_scrape_all_pages_single_page(self, mock_scrape):
        """Test scraping satu halaman saja"""
        mock_scrape.return_value = [
            {
                'title': 'Single Product',
                'price': '$50.00',
                'rating': 'Rating: ⭐ 5.0 / 5',
                'colors': '1 Colors',
                'size': 'Size: M',
                'gender': 'Gender: Men',
                'timestamp': datetime.now().isoformat()
            }
        ]
        
        result = scrape_all_pages(start_page=1, end_page=1)
        
        assert len(result) == 1
        assert mock_scrape.call_count == 1
    
    @patch('utils.extract.scrape_page')
    def test_scrape_all_pages_multiple_products_per_page(self, mock_scrape):
        """Test scraping dengan beberapa produk per halaman"""
        mock_scrape.return_value = [
            {
                'title': f'Product {i}',
                'price': f'${i*10}.00',
                'rating': f'Rating: ⭐ {i}.0 / 5',
                'colors': f'{i} Colors',
                'size': 'Size: M',
                'gender': 'Gender: Men',
                'timestamp': datetime.now().isoformat()
            }
            for i in range(1, 21)
        ]
        
        result = scrape_all_pages(start_page=1, end_page=2)
        
        assert len(result) == 40
    
    @patch('utils.extract.scrape_page')
    def test_scrape_all_pages_generic_exception(self, mock_scrape):
        """Test scraping ketika terjadi error generik (bukan RequestException)"""
        mock_scrape.side_effect = TypeError("Unexpected type error")
        
        with pytest.raises(ValueError, match="No products were scraped"):
            scrape_all_pages(start_page=1, end_page=1)
            
    @patch('utils.extract.requests.get')
    def test_scrape_page_generic_unexpected_exception(self, mock_get):
        """Test handling error yang benar-benar tidak terduga di scrape_page"""
        mock_response = MagicMock()
        mock_response.text = MOCK_HTML_SINGLE
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Mock get_text untuk menghasilkan error
        type(mock_response).text = property(lambda self: (_ for _ in ()).throw(RuntimeError("Text parsing error")))
        
        with pytest.raises(Exception):
            scrape_page(1)