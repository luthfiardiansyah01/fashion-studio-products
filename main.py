"""
Main script untuk menjalankan ETL Pipeline.
"""

import logging
from utils.extract import scrape_all_pages
from utils.transform import transform_data
from utils.load import load_data

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """
    Fungsi utama untuk menjalankan ETL Pipeline.
    """
    try:
        logger.info("=" * 60)
        logger.info("STARTING ETL PIPELINE - Fashion Studio Data Scraping")
        logger.info("=" * 60)
        
        # =====================
        # EXTRACT PHASE
        # =====================
        logger.info("\n" + "=" * 60)
        logger.info("[EXTRACT] Starting data extraction...")
        logger.info("=" * 60)
        
        raw_df = scrape_all_pages(start_page=1, end_page=50)
        logger.info(f"[EXTRACT] Successfully extracted {len(raw_df)} raw records")
        
        # =====================
        # TRANSFORM PHASE
        # =====================
        logger.info("\n" + "=" * 60)
        logger.info("[TRANSFORM] Starting data transformation...")
        logger.info("=" * 60)
        
        clean_df = transform_data(raw_df)
        logger.info(f"[TRANSFORM] Successfully transformed {len(clean_df)} clean records")
        
        # Tampilkan sample data
        logger.info("\n[TRANSFORM] Sample of transformed data:")
        logger.info(clean_df.head().to_string())
        
        # Tampilkan info tipe data
        logger.info("\n[TRANSFORM] Data types:")
        for col in clean_df.columns:
            logger.info(f"  - {col}: {clean_df[col].dtype}")
        
        # =====================
        # LOAD PHASE
        # =====================
        logger.info("\n" + "=" * 60)
        logger.info("[LOAD] Starting data loading...")
        logger.info("=" * 60)
        
        results = load_data(
            clean_df,
            save_csv=True,
            save_sheets=True,   # Set ke True jika memiliki Google Sheets credentials
            save_postgres=True  # Set ke True jika memiliki PostgreSQL yang dikonfigurasi
        )
        
        logger.info(f"[LOAD] Load results:")
        for repo, status in results.items():
            logger.info(f"  - {repo}: {status}")
        
        # =====================
        # SUMMARY
        # =====================
        logger.info("\n" + "=" * 60)
        logger.info("ETL PIPELINE COMPLETED SUCCESSFULLY!")
        logger.info("=" * 60)
        logger.info(f"\nSummary:")
        logger.info(f"  - Raw records extracted: {len(raw_df)}")
        logger.info(f"  - Clean records after transformation: {len(clean_df)}")
        logger.info(f"  - Records removed during transformation: {len(raw_df) - len(clean_df)}")
        
    except ValueError as e:
        logger.error(f"Value error in ETL Pipeline: {e}")
        raise
    except KeyError as e:
        logger.error(f"Key error in ETL Pipeline: {e}")
        raise
    except Exception as e:
        logger.error(f"ETL Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    main()