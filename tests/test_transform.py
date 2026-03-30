"""
Unit tests untuk module transform.py
"""

import pytest
import pandas as pd
from unittest.mock import patch
from utils.transform import (
    convert_price_to_idr,
    clean_rating,
    clean_colors,
    clean_size,
    clean_gender,
    remove_invalid_products,
    remove_duplicates,
    remove_nulls,
    convert_data_types,
    transform_data,
    EXCHANGE_RATE
)


class TestConvertPriceToIdr:
    """Tests untuk fungsi convert_price_to_idr"""
    
    def test_convert_valid_price(self):
        """Test konversi harga valid"""
        result = convert_price_to_idr("$25.00")
        expected = 25.00 * EXCHANGE_RATE
        assert result == expected
    
    def test_convert_price_without_dollar_sign(self):
        """Test konversi harga tanpa tanda $"""
        result = convert_price_to_idr("25.00")
        expected = 25.00 * EXCHANGE_RATE
        assert result == expected
    
    def test_convert_price_with_whitespace(self):
        """Test konversi harga dengan whitespace"""
        result = convert_price_to_idr(" $ 30.00 ")
        expected = 30.00 * EXCHANGE_RATE
        assert result == expected
    
    def test_convert_price_integer(self):
        """Test konversi harga integer"""
        result = convert_price_to_idr("$50")
        expected = 50.00 * EXCHANGE_RATE
        assert result == expected
    
    def test_convert_price_zero(self):
        """Test konversi harga nol"""
        result = convert_price_to_idr("$0.00")
        assert result == 0.0
    
    def test_convert_price_large_value(self):
        """Test konversi harga besar"""
        result = convert_price_to_idr("$1000.00")
        expected = 1000.00 * EXCHANGE_RATE
        assert result == expected
    
    def test_convert_price_with_cents(self):
        """Test konversi harga dengan sen"""
        result = convert_price_to_idr("$25.99")
        expected = 25.99 * EXCHANGE_RATE
        assert result == expected
    
    def test_convert_price_invalid_string(self):
        """Test konversi harga string tidak valid"""
        result = convert_price_to_idr("invalid")
        assert result is None
    
    def test_convert_price_none(self):
        """Test konversi harga None"""
        result = convert_price_to_idr(None)
        assert result is None
    
    def test_convert_price_empty_string(self):
        """Test konversi harga string kosong"""
        result = convert_price_to_idr("")
        assert result is None
    
    def test_convert_price_negative(self):
        """Test konversi harga negatif"""
        result = convert_price_to_idr("$-10.00")
        expected = -10.00 * EXCHANGE_RATE
        assert result == expected


class TestCleanRating:
    """Tests untuk fungsi clean_rating"""
    
    def test_clean_rating_valid(self):
        """Test pembersihan rating valid"""
        result = clean_rating("4.8 / 5")
        assert result == 4.8
    
    def test_clean_rating_integer_value(self):
        """Test pembersihan rating integer"""
        result = clean_rating("5 / 5")
        assert result == 5.0
    
    def test_clean_rating_low_value(self):
        """Test pembersihan rating rendah"""
        result = clean_rating("1.0 / 5")
        assert result == 1.0
    
    def test_clean_rating_invalid_rating_string(self):
        """Test pembersihan 'Invalid Rating'"""
        result = clean_rating("Invalid Rating")
        assert result is None
    
    def test_clean_rating_none(self):
        """Test pembersihan None"""
        result = clean_rating(None)
        assert result is None
    
    def test_clean_rating_empty_string(self):
        """Test pembersihan string kosong"""
        result = clean_rating("")
        assert result is None
    
    def test_clean_rating_just_number(self):
        """Test pembersihan hanya angka"""
        result = clean_rating("4.5")
        assert result == 4.5
    
    def test_clean_rating_with_whitespace(self):
        """Test pembersihan rating dengan whitespace"""
        result = clean_rating("  4.8 / 5  ")
        assert result == 4.8
    
    def test_clean_rating_invalid_string(self):
        """Test pembersihan string tidak valid"""
        result = clean_rating("no rating")
        assert result is None


class TestCleanColors:
    """Tests untuk fungsi clean_colors"""
    
    def test_clean_colors_valid(self):
        """Test pembersihan colors valid"""
        result = clean_colors("3 Colors")
        assert result == 3
    
    def test_clean_colors_one_color(self):
        """Test pembersihan satu warna"""
        result = clean_colors("1 Color")
        assert result == 1
    
    def test_clean_colors_just_number(self):
        """Test pembersihan hanya angka"""
        result = clean_colors("5")
        assert result == 5
    
    def test_clean_colors_none(self):
        """Test pembersihan None"""
        result = clean_colors(None)
        assert result is None
    
    def test_clean_colors_empty_string(self):
        """Test pembersihan string kosong"""
        result = clean_colors("")
        assert result is None
    
    def test_clean_colors_large_number(self):
        """Test pembersihan jumlah warna besar"""
        result = clean_colors("100 Colors")
        assert result == 100
    
    def test_clean_colors_zero(self):
        """Test pembersihan nol warna"""
        result = clean_colors("0 Colors")
        assert result == 0


class TestCleanSize:
    """Tests untuk fungsi clean_size"""
    
    def test_clean_size_valid(self):
        """Test pembersihan size valid"""
        result = clean_size("Size: M, L, XL")
        assert result == "M, L, XL"
    
    def test_clean_size_without_prefix(self):
        """Test pembersihan size tanpa prefix"""
        result = clean_size("M, L, XL")
        assert result == "M, L, XL"
    
    def test_clean_size_single_size(self):
        """Test pembersihan satu ukuran"""
        result = clean_size("Size: M")
        assert result == "M"
    
    def test_clean_size_none(self):
        """Test pembersihan None"""
        result = clean_size(None)
        assert result is None
    
    def test_clean_size_empty(self):
        """Test pembersihan string kosong"""
        result = clean_size("")
        assert result is None
    
    def test_clean_size_only_prefix(self):
        """Test pembersihan size hanya prefix"""
        result = clean_size("Size: ")
        assert result is None
    
    def test_clean_size_with_whitespace(self):
        """Test pembersihan size dengan whitespace"""
        result = clean_size("  Size:  M, L  ")
        assert result == "M, L"


class TestCleanGender:
    """Tests untuk fungsi clean_gender"""
    
    def test_clean_gender_men(self):
        """Test pembersihan gender Men"""
        result = clean_gender("Gender: Men")
        assert result == "Men"
    
    def test_clean_gender_women(self):
        """Test pembersihan gender Women"""
        result = clean_gender("Gender: Women")
        assert result == "Women"
    
    def test_clean_gender_unisex(self):
        """Test pembersihan gender Unisex"""
        result = clean_gender("Gender: Unisex")
        assert result == "Unisex"
    
    def test_clean_gender_without_prefix(self):
        """Test pembersihan gender tanpa prefix"""
        result = clean_gender("Men")
        assert result == "Men"
    
    def test_clean_gender_none(self):
        """Test pembersihan None"""
        result = clean_gender(None)
        assert result is None
    
    def test_clean_gender_empty(self):
        """Test pembersihan string kosong"""
        result = clean_gender("")
        assert result is None
    
    def test_clean_gender_only_prefix(self):
        """Test pembersihan gender hanya prefix"""
        result = clean_gender("Gender: ")
        assert result is None
    
    def test_clean_gender_with_whitespace(self):
        """Test pembersihan gender dengan whitespace"""
        result = clean_gender("  Gender:  Men  ")
        assert result == "Men"


class TestRemoveInvalidProducts:
    """Tests untuk fungsi remove_invalid_products"""
    
    def test_remove_unknown_products(self):
        """Test menghapus Unknown Product"""
        df = pd.DataFrame({
            'title': ['T-Shirt', 'Unknown Product', 'Jacket'],
            'price': ['$25.00', '$10.00', '$50.00']
        })
        
        result = remove_invalid_products(df)
        
        assert len(result) == 2
        assert 'Unknown Product' not in result['title'].values
    
    def test_no_unknown_products(self):
        """Test ketika tidak ada Unknown Product"""
        df = pd.DataFrame({
            'title': ['T-Shirt', 'Jacket'],
            'price': ['$25.00', '$50.00']
        })
        
        result = remove_invalid_products(df)
        
        assert len(result) == 2
    
    def test_all_unknown_products(self):
        """Test ketika semua produk adalah Unknown Product"""
        df = pd.DataFrame({
            'title': ['Unknown Product', 'Unknown Product'],
            'price': ['$10.00', '$20.00']
        })
        
        result = remove_invalid_products(df)
        
        assert len(result) == 0


class TestRemoveDuplicates:
    """Tests untuk fungsi remove_duplicates"""
    
    def test_remove_duplicates_success(self):
        """Test menghapus duplikat"""
        df = pd.DataFrame({
            'title': ['T-Shirt', 'T-Shirt', 'Jacket'],
            'price': ['$25.00', '$25.00', '$50.00']
        })
        
        result = remove_duplicates(df)
        
        assert len(result) == 2
    
    def test_no_duplicates(self):
        """Test ketika tidak ada duplikat"""
        df = pd.DataFrame({
            'title': ['T-Shirt', 'Jacket', 'Pants'],
            'price': ['$25.00', '$50.00', '$30.00']
        })
        
        result = remove_duplicates(df)
        
        assert len(result) == 3


class TestRemoveNulls:
    """Tests untuk fungsi remove_nulls"""
    
    def test_remove_nulls_success(self):
        """Test menghapus baris dengan null"""
        df = pd.DataFrame({
            'title': ['T-Shirt', None, 'Jacket'],
            'price': ['$25.00', '$30.00', '$50.00']
        })
        
        result = remove_nulls(df)
        
        assert len(result) == 2
        assert result['title'].isna().sum() == 0
    
    def test_no_nulls(self):
        """Test ketika tidak ada null"""
        df = pd.DataFrame({
            'title': ['T-Shirt', 'Jacket'],
            'price': ['$25.00', '$50.00']
        })
        
        result = remove_nulls(df)
        
        assert len(result) == 2


class TestConvertDataTypes:
    """Tests untuk fungsi convert_data_types"""
    
    def test_convert_data_types_success(self):
        """Test konversi tipe data berhasil"""
        df = pd.DataFrame({
            'title': ['T-Shirt'],
            'price': [400000.0],
            'rating': [4.8],
            'colors': [3],
            'size': ['M'],
            'gender': ['Men']
        })
        
        result = convert_data_types(df)
        
        assert result['price'].dtype == float
        assert result['rating'].dtype == float
        assert result['colors'].dtype == int
        assert result['size'].dtype == object
        assert result['gender'].dtype == object
        assert result['title'].dtype == object
    
    def test_convert_data_types_missing_column(self):
        """Test konversi tipe data dengan kolom yang hilang"""
        df = pd.DataFrame({
            'title': ['T-Shirt'],
            'price': [400000.0]
        })
        
        with pytest.raises(KeyError):
            convert_data_types(df)


class TestTransformData:
    """Tests untuk fungsi transform_data"""
    
    def test_transform_data_valid(self):
        """Test transformasi data valid"""
        df = pd.DataFrame({
            'title': ['T-Shirt', 'Jacket'],
            'price': ['$25.00', '$50.00'],
            'rating': ['4.8 / 5', '4.0 / 5'],
            'colors': ['3 Colors', '5 Colors'],
            'size': ['Size: M, L', 'Size: S, M, L'],
            'gender': ['Gender: Men', 'Gender: Women'],
            'timestamp': ['2024-01-01T12:00:00', '2024-01-01T12:00:00']
        })
        
        result = transform_data(df)
        
        assert len(result) == 2
        assert result['price'].dtype == float
        assert result['rating'].dtype == float
        assert result['colors'].dtype == int
        assert result['size'].dtype == object
        assert result['gender'].dtype == object
        assert result.loc[0, 'price'] == 25.00 * EXCHANGE_RATE
        assert result.loc[0, 'rating'] == 4.8
        assert result.loc[0, 'colors'] == 3
        assert result.loc[0, 'size'] == 'M, L'
        assert result.loc[0, 'gender'] == 'Men'
    
    def test_transform_data_remove_duplicates(self):
        """Test menghapus duplikat dalam transformasi"""
        df = pd.DataFrame({
            'title': ['T-Shirt', 'T-Shirt'],
            'price': ['$25.00', '$25.00'],
            'rating': ['4.8 / 5', '4.8 / 5'],
            'colors': ['3 Colors', '3 Colors'],
            'size': ['Size: M', 'Size: M'],
            'gender': ['Gender: Men', 'Gender: Men'],
            'timestamp': ['2024-01-01T12:00:00', '2024-01-01T12:00:00']
        })
        
        result = transform_data(df)
        
        assert len(result) == 1
    
    def test_transform_data_remove_nulls(self):
        """Test menghapus null dalam transformasi"""
        df = pd.DataFrame({
            'title': ['T-Shirt', None],
            'price': ['$25.00', '$30.00'],
            'rating': ['4.8 / 5', '4.0 / 5'],
            'colors': ['3 Colors', '2 Colors'],
            'size': ['Size: M', 'Size: L'],
            'gender': ['Gender: Men', 'Gender: Women'],
            'timestamp': ['2024-01-01T12:00:00', '2024-01-01T12:00:00']
        })
        
        result = transform_data(df)
        
        assert len(result) == 1
        assert result.loc[0, 'title'] == 'T-Shirt'
    
    def test_transform_data_remove_invalid_product(self):
        """Test menghapus Unknown Product dalam transformasi"""
        df = pd.DataFrame({
            'title': ['T-Shirt', 'Unknown Product', 'Jacket'],
            'price': ['$25.00', '$10.00', '$50.00'],
            'rating': ['4.8 / 5', 'Invalid Rating', '4.0 / 5'],
            'colors': ['3 Colors', '1 Colors', '5 Colors'],
            'size': ['Size: M', 'Size: S', 'Size: L'],
            'gender': ['Gender: Men', 'Gender: Unisex', 'Gender: Women'],
            'timestamp': ['2024-01-01T12:00:00', '2024-01-01T12:00:00', '2024-01-01T12:00:00']
        })
        
        result = transform_data(df)
        
        assert len(result) == 2
        assert 'Unknown Product' not in result['title'].values
    
    def test_transform_data_empty_dataframe(self):
        """Test transformasi DataFrame kosong"""
        df = pd.DataFrame()
        
        with pytest.raises(ValueError, match="Input DataFrame is empty"):
            transform_data(df)
    
    def test_transform_data_invalid_rating_removed(self):
        """Test rating invalid dihapus dalam transformasi"""
        df = pd.DataFrame({
            'title': ['T-Shirt', 'Jacket'],
            'price': ['$25.00', '$50.00'],
            'rating': ['Invalid Rating', '4.0 / 5'],
            'colors': ['3 Colors', '5 Colors'],
            'size': ['Size: M', 'Size: L'],
            'gender': ['Gender: Men', 'Gender: Women'],
            'timestamp': ['2024-01-01T12:00:00', '2024-01-01T12:00:00']
        })
        
        result = transform_data(df)
        
        assert len(result) == 1
        assert result.loc[0, 'title'] == 'Jacket'
    
    def test_transform_data_missing_column(self):
        """Test transformasi dengan kolom yang hilang"""
        df = pd.DataFrame({
            'title': ['T-Shirt'],
            'price': ['$25.00']
        })
        
        with pytest.raises(KeyError):
            transform_data(df)
    
    def test_transform_data_preserves_timestamp(self):
        """Test bahwa timestamp dipertahankan"""
        df = pd.DataFrame({
            'title': ['T-Shirt'],
            'price': ['$25.00'],
            'rating': ['4.8 / 5'],
            'colors': ['3 Colors'],
            'size': ['Size: M'],
            'gender': ['Gender: Men'],
            'timestamp': ['2024-01-01T12:00:00.000000']
        })
        
        result = transform_data(df)
        
        assert result.loc[0, 'timestamp'] == '2024-01-01T12:00:00.000000'
    
    def test_transform_data_index_reset(self):
        """Test bahwa index direset setelah transformasi"""
        df = pd.DataFrame({
            'title': ['T-Shirt', 'Unknown Product', 'Jacket'],
            'price': ['$25.00', '$10.00', '$50.00'],
            'rating': ['4.8 / 5', 'Invalid Rating', '4.0 / 5'],
            'colors': ['3 Colors', '1 Colors', '5 Colors'],
            'size': ['Size: M', 'Size: S', 'Size: L'],
            'gender': ['Gender: Men', 'Gender: Unisex', 'Gender: Women'],
            'timestamp': ['2024-01-01T12:00:00', '2024-01-01T12:00:00', '2024-01-01T12:00:00']
        })
        
        result = transform_data(df)
        
        assert list(result.index) == [0, 1]

    def test_transform_data_generic_exception(self):
        """Test error generik di transform_data (bukan ValueError/KeyError)"""
        df = pd.DataFrame({
            'title': ['T-Shirt'],
            'price': ['$25.00'],
            'rating': ['4.8 / 5'],
            'colors': ['3 Colors'],
            'size': ['Size: M'],
            'gender': ['Gender: Men'],
            'timestamp': ['2024-01-01T12:00:00']
        })
        
        # Mock remove_invalid_products untuk raise error generik
        with patch('utils.transform.remove_invalid_products', side_effect=RuntimeError("DB Error")):
            with pytest.raises(RuntimeError):
                transform_data(df)

    def test_convert_data_types_type_error(self):
        """Test konversi tipe data gagal karena TypeError"""
        df = pd.DataFrame({
            'title': ['T-Shirt'],
            'price': ["bukan_angka"],  # Akan error saat diastype float
            'rating': [4.8],
            'colors': [3],
            'size': ['M'],
            'gender': ['Men']
        })
        
        with pytest.raises((ValueError, TypeError)):
            convert_data_types(df)

class TestErrorHandlingHelpers:
    """Tests tambahan untuk error handling di fungsi helper"""

    def test_remove_invalid_products_unexpected_error(self):
        """Test error pada remove_invalid_products"""
        # Membuat dataframe yang akan error saat dioperasikan (menggunakan None)
        df = None
        with pytest.raises(Exception):
            remove_invalid_products(df)

    def test_remove_duplicates_unexpected_error(self):
        """Test error pada remove_duplicates"""
        df = None
        with pytest.raises(Exception):
            remove_duplicates(df)

    def test_remove_nulls_unexpected_error(self):
        """Test error pada remove_nulls"""
        df = None
        with pytest.raises(Exception):
            remove_nulls(df)