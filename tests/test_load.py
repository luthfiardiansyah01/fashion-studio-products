"""
Unit tests untuk module load.py
"""

import pytest
import pandas as pd
import os
import tempfile
from unittest.mock import patch, MagicMock
from utils.load import (
    save_to_csv,
    save_to_google_sheets,
    save_to_postgresql,
    load_data,
    CSV_FILE_PATH,
    GOOGLE_SHEETS_CREDENTIALS_PATH,
    GOOGLE_SHEET_NAME,
    TABLE_NAME,
    GSPREAD_AVAILABLE,
    PSYCOPG2_AVAILABLE
)


# Fixture untuk DataFrame test
@pytest.fixture
def sample_df():
    """Fixture untuk DataFrame sample"""
    return pd.DataFrame({
        'title': ['T-Shirt', 'Jacket', 'Pants'],
        'price': [400000.0, 800000.0, 480000.0],
        'rating': [4.8, 4.0, 4.5],
        'colors': [3, 5, 2],
        'size': ['M, L', 'S, M', 'L, XL'],
        'gender': ['Men', 'Women', 'Men'],
        'timestamp': ['2024-01-01T12:00:00', '2024-01-01T12:00:00', '2024-01-01T12:00:00']
    })


@pytest.fixture
def single_row_df():
    """Fixture untuk DataFrame dengan satu baris"""
    return pd.DataFrame({
        'title': ['T-Shirt'],
        'price': [400000.0],
        'rating': [4.8],
        'colors': [3],
        'size': ['M'],
        'gender': ['Men'],
        'timestamp': ['2024-01-01T12:00:00']
    })


class TestSaveToCsv:
    """Tests untuk fungsi save_to_csv"""
    
    def test_save_to_csv_success(self, tmp_path, sample_df):
        """Test penyimpanan CSV berhasil"""
        file_path = os.path.join(tmp_path, "test_products.csv")
        result = save_to_csv(sample_df, file_path)
        
        assert result is True
        assert os.path.exists(file_path)
        
        # Verifikasi konten
        loaded_df = pd.read_csv(file_path)
        assert len(loaded_df) == 3
        assert list(loaded_df.columns) == list(sample_df.columns)
    
    def test_save_to_csv_single_row(self, tmp_path, single_row_df):
        """Test penyimpanan CSV dengan satu baris"""
        file_path = os.path.join(tmp_path, "single_product.csv")
        result = save_to_csv(single_row_df, file_path)
        
        assert result is True
        loaded_df = pd.read_csv(file_path)
        assert len(loaded_df) == 1
    
    def test_save_to_csv_empty_dataframe(self, tmp_path):
        """Test penyimpanan DataFrame kosong"""
        df = pd.DataFrame()
        file_path = os.path.join(tmp_path, "test_products.csv")
        
        with pytest.raises(ValueError, match="DataFrame is empty"):
            save_to_csv(df, file_path)
    
    def test_save_to_csv_creates_directory(self, tmp_path):
        """Test bahwa direktori dibuat jika tidak ada"""
        df = pd.DataFrame({
            'title': ['T-Shirt'],
            'price': [400000.0],
            'rating': [4.8],
            'colors': [3],
            'size': ['M'],
            'gender': ['Men'],
            'timestamp': ['2024-01-01T12:00:00']
        })
        
        file_path = os.path.join(tmp_path, "subdir", "nested", "products.csv")
        result = save_to_csv(df, file_path)
        
        assert result is True
        assert os.path.exists(file_path)
    
    def test_save_to_csv_overwrite_existing(self, tmp_path, sample_df):
        """Test menimpa file yang sudah ada"""
        file_path = os.path.join(tmp_path, "products.csv")
        
        # Buat file awal
        save_to_csv(sample_df, file_path)
        
        # Buat DataFrame baru dan simpan
        new_df = sample_df.iloc[:1]
        save_to_csv(new_df, file_path)
        
        loaded_df = pd.read_csv(file_path)
        assert len(loaded_df) == 1

    def test_save_to_csv_os_error(self, tmp_path, sample_df):
        """Test handling OS error saat menulis CSV"""
        file_path = os.path.join(tmp_path, "test.csv")
        
        # Mock builtin open untuk raise OSError
        with patch('builtins.open', side_effect=OSError("Disk full")):
            with pytest.raises(OSError):
                save_to_csv(sample_df, file_path)


class TestSaveToGoogleSheets:
    """Tests untuk fungsi save_to_google_sheets"""
    
    @patch('utils.load.gspread')
    @patch('utils.load.Credentials')
    @patch('utils.load.GSPREAD_AVAILABLE', True)
    def test_save_to_google_sheets_success(self, mock_creds, mock_gspread, sample_df, tmp_path):
        """Test penyimpanan ke Google Sheets berhasil"""
        # Buat file credentials palsu
        creds_path = os.path.join(tmp_path, "fake_creds.json")
        with open(creds_path, 'w') as f:
            f.write('{}')
        
        # Mock gspread operations
        mock_client = MagicMock()
        mock_gspread.authorize.return_value = mock_client
        
        mock_spreadsheet = MagicMock()
        mock_client.open.return_value = mock_spreadsheet
        
        mock_worksheet = MagicMock()
        mock_spreadsheet.sheet1 = mock_worksheet
        
        result = save_to_google_sheets(sample_df, creds_path)
        
        assert result is True
        mock_worksheet.clear.assert_called_once()
        mock_worksheet.update.assert_called_once()
    
    @patch('utils.load.GSPREAD_AVAILABLE', True)
    def test_save_to_google_sheets_empty_dataframe(self, sample_df):
        """Test penyimpanan DataFrame kosong ke Google Sheets"""
        df = pd.DataFrame()
        
        with pytest.raises(ValueError, match="DataFrame is empty"):
            save_to_google_sheets(df)
    
    @patch('utils.load.GSPREAD_AVAILABLE', True)
    def test_save_to_google_sheets_missing_credentials(self, sample_df):
        """Test handling credentials file tidak ditemukan"""
        with pytest.raises(FileNotFoundError):
            save_to_google_sheets(sample_df, 'nonexistent_credentials.json')
    
    @patch('utils.load.GSPREAD_AVAILABLE', False)
    def test_save_to_google_sheets_gspread_not_installed(self, sample_df):
        """Test handling gspread tidak terinstal"""
        with pytest.raises(ImportError, match="gspread library is not installed"):
            save_to_google_sheets(sample_df)
    
    @patch('utils.load.gspread')
    @patch('utils.load.Credentials')
    @patch('utils.load.GSPREAD_AVAILABLE', True)
    def test_save_to_google_sheets_create_new_spreadsheet(self, mock_creds, mock_gspread, sample_df, tmp_path):
        """Test membuat spreadsheet baru jika tidak ditemukan"""
        import utils.load
        utils.load.gspread = mock_gspread
        
        creds_path = os.path.join(tmp_path, "fake_creds.json")
        with open(creds_path, 'w') as f:
            f.write('{}')
        
        mock_client = MagicMock()
        mock_gspread.authorize.return_value = mock_client
        
        # Spreadsheet not found, then create
        mock_gspread.SpreadsheetNotFound = Exception
        mock_client.open.side_effect = mock_gspread.SpreadsheetNotFound("Not found")
        
        mock_spreadsheet = MagicMock()
        mock_client.create.return_value = mock_spreadsheet
        
        mock_worksheet = MagicMock()
        mock_spreadsheet.sheet1 = mock_worksheet
        
        result = save_to_google_sheets(sample_df, creds_path)
        
        assert result is True
        mock_client.create.assert_called_once_with(GOOGLE_SHEET_NAME)
        mock_spreadsheet.share.assert_called_once()

    @patch('utils.load.gspread')
    @patch('utils.load.Credentials')
    @patch('utils.load.GSPREAD_AVAILABLE', True)
    def test_save_to_google_sheets_gspread_exception(self, mock_creds, mock_gspread, sample_df, tmp_path):
        """Test handling GSpread specific exception"""
        import utils.load
        utils.load.gspread = mock_gspread
        
        creds_path = os.path.join(tmp_path, "fake_creds.json")
        with open(creds_path, 'w') as f:
            f.write('{}')
        
        mock_client = MagicMock()
        mock_gspread.authorize.return_value = mock_client
        
        # Mock spreadsheet yang raise GSpreadException saat update
        mock_gspread.GSpreadException = Exception
        mock_spreadsheet = MagicMock()
        mock_client.open.return_value = mock_spreadsheet
        mock_spreadsheet.sheet1.update.side_effect = utils.load.gspread.GSpreadException("Spreadsheet error")
        
        with pytest.raises(Exception):
            save_to_google_sheets(sample_df, creds_path)


class TestSaveToPostgresql:
    """Tests untuk fungsi save_to_postgresql"""
    
    @patch('utils.load.psycopg2')
    @patch('utils.load.PSYCOPG2_AVAILABLE', True)
    def test_save_to_postgresql_success(self, mock_psycopg2, sample_df):
        """Test penyimpanan ke PostgreSQL berhasil"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_psycopg2.connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [3]
        
        with patch.dict(os.environ, {
            'DB_HOST': 'localhost',
            'DB_PORT': '5432',
            'DB_NAME': 'test_db',
            'DB_USER': 'test_user',
            'DB_PASSWORD': 'test_password'
        }):
            result = save_to_postgresql(sample_df)
        
        assert result is True
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()
        
        # Pastikan pemanggilan connect SEKARANG menyertakan sslmode='require'
        mock_psycopg2.connect.assert_called_once_with(
            host='localhost',
            port='5432',
            dbname='test_db',
            user='test_user',
            password='test_password',
            sslmode='require'
        )
    
    @patch('utils.load.PSYCOPG2_AVAILABLE', True)
    def test_save_to_postgresql_empty_dataframe(self):
        """Test penyimpanan DataFrame kosong ke PostgreSQL"""
        df = pd.DataFrame()
        
        with pytest.raises(ValueError, match="DataFrame is empty"):
            save_to_postgresql(df)
    
    @patch('utils.load.PSYCOPG2_AVAILABLE', False)
    def test_save_to_postgresql_psycopg2_not_installed(self, sample_df):
        """Test handling psycopg2 tidak terinstal"""
        with pytest.raises(ImportError, match="psycopg2 library is not installed"):
            save_to_postgresql(sample_df)
    
    @patch('utils.load.psycopg2')
    @patch('utils.load.PSYCOPG2_AVAILABLE', True)
    def test_save_to_postgresql_connection_error(self, mock_psycopg2, sample_df):
        """Test handling error koneksi PostgreSQL"""
        import psycopg2
        mock_psycopg2.OperationalError = psycopg2.OperationalError
        mock_psycopg2.connect.side_effect = psycopg2.OperationalError("Connection failed")
        
        with pytest.raises(psycopg2.OperationalError):
            save_to_postgresql(sample_df)
    
    @patch('utils.load.psycopg2')
    @patch('utils.load.PSYCOPG2_AVAILABLE', True)
    def test_save_to_postgresql_uses_env_variables(self, mock_psycopg2, sample_df):
        """Test bahwa environment variables digunakan"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_psycopg2.connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [3]
        
        with patch.dict(os.environ, {
            'DB_HOST': 'custom_host',
            'DB_PORT': '5433',
            'DB_NAME': 'custom_db',
            'DB_USER': 'custom_user',
            'DB_PASSWORD': 'custom_password'
        }):
            save_to_postgresql(sample_df)
        
        # DIPERBAIKI: Disesuaikan dengan kode load.py yang sekarang menggunakan sslmode='require'
        mock_psycopg2.connect.assert_called_once_with(
            host='custom_host',
            port='5433',
            dbname='custom_db',
            user='custom_user',
            password='custom_password',
            sslmode='require'
        )

    @patch('utils.load.psycopg2')
    @patch('utils.load.PSYCOPG2_AVAILABLE', True)
    def test_save_to_postgresql_programming_error(self, mock_psycopg2, sample_df):
        """Test handling programming error PostgreSQL (misal: query salah)"""
        # 1. Buat SEMUA kelas Exception palsu yang ada di except block load.py
        class MockOperationalError(Exception): pass
        class MockProgrammingError(Exception): pass
        class MockDbError(Exception): pass

        # 2. Tempelkan SEMUANYA ke mock psycopg2
        mock_psycopg2.OperationalError = MockOperationalError
        mock_psycopg2.ProgrammingError = MockProgrammingError
        mock_psycopg2.Error = MockDbError

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_psycopg2.connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # 3. Trigger error
        mock_cursor.execute.side_effect = MockProgrammingError("Invalid SQL")
        
        with pytest.raises(MockProgrammingError):
            save_to_postgresql(sample_df)
            
    @patch('utils.load.psycopg2')
    @patch('utils.load.PSYCOPG2_AVAILABLE', True)
    def test_save_to_postgresql_generic_psycopg2_error(self, mock_psycopg2, sample_df):
        """Test handling generic psycopg2 Error"""
        # 1. Buat SEMUA kelas Exception palsu yang ada di except block load.py
        class MockOperationalError(Exception): pass
        class MockProgrammingError(Exception): pass
        class MockDbError(Exception): pass

        # 2. Tempelkan SEMUANYA ke mock psycopg2
        mock_psycopg2.OperationalError = MockOperationalError
        mock_psycopg2.ProgrammingError = MockProgrammingError
        mock_psycopg2.Error = MockDbError
        
        # 3. Trigger error
        mock_psycopg2.connect.side_effect = MockDbError("Custom DB error")
        
        with pytest.raises(MockDbError):
            save_to_postgresql(sample_df)


class TestLoadData:
    """Tests untuk fungsi load_data"""
    
    def test_load_data_csv_only(self, tmp_path, sample_df):
        """Test loading hanya ke CSV"""
        file_path = os.path.join(tmp_path, "test.csv")
        
        with patch('utils.load.CSV_FILE_PATH', file_path):
            result = load_data(sample_df, save_csv=True, save_sheets=False, save_postgres=False)
        
        assert result['csv'] is True
        assert result['google_sheets'] is None
        assert result['postgresql'] is None
    
    @patch('utils.load.save_to_google_sheets')
    def test_load_data_with_google_sheets_error(self, mock_sheets, tmp_path, sample_df):
        """Test handling error Google Sheets dalam load_data"""
        mock_sheets.side_effect = Exception("Sheets error")
        
        file_path = os.path.join(tmp_path, "test.csv")
        
        with patch('utils.load.CSV_FILE_PATH', file_path):
            result = load_data(sample_df, save_csv=True, save_sheets=True, save_postgres=False)
        
        assert result['csv'] is True
        assert result['google_sheets'] is False
    
    @patch('utils.load.save_to_postgresql')
    def test_load_data_with_postgres_error(self, mock_postgres, tmp_path, sample_df):
        """Test handling error PostgreSQL dalam load_data"""
        mock_postgres.side_effect = Exception("Postgres error")
        
        file_path = os.path.join(tmp_path, "test.csv")
        
        with patch('utils.load.CSV_FILE_PATH', file_path):
            result = load_data(sample_df, save_csv=True, save_sheets=False, save_postgres=True)
        
        assert result['csv'] is True
        assert result['postgresql'] is False
    
    def test_load_data_none_options(self, sample_df):
        """Test loading tanpa opsi apapun"""
        result = load_data(sample_df, save_csv=False, save_sheets=False, save_postgres=False)
        
        assert result['csv'] is None
        assert result['google_sheets'] is None
        assert result['postgresql'] is None
    
    @patch('utils.load.save_to_google_sheets', return_value=True)
    @patch('utils.load.save_to_postgresql', return_value=True)
    def test_load_data_all_options_success(self, mock_postgres, mock_sheets, tmp_path, sample_df):
        """Test loading ke semua repositori berhasil"""
        file_path = os.path.join(tmp_path, "test.csv")
        
        with patch('utils.load.CSV_FILE_PATH', file_path):
            result = load_data(sample_df, save_csv=True, save_sheets=True, save_postgres=True)
        
        assert result['csv'] is True
        assert result['google_sheets'] is True
        assert result['postgresql'] is True

    @patch('utils.load.save_to_csv')
    def test_load_data_generic_exception_in_csv(self, mock_csv, sample_df):
        """Test handling generic exception di fungsi utama load_data"""
        mock_csv.side_effect = RuntimeError("Unexpected crash")
        
        with pytest.raises(RuntimeError):
            load_data(sample_df, save_csv=True, save_sheets=False, save_postgres=False)