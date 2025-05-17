import asyncio
import logging
from scraper.processor import scraper_processor
from database.db_manager import database, create_db_and_tables

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def clear_database():
    """Clear all data from the database"""
    logger.info("Clearing database...")
    await database.execute("DELETE FROM product_images")
    await database.execute("DELETE FROM products")
    logger.info("Database cleared")

async def test_scraper():
    try:
        # Initialize database
        logger.info("Initializing database...")
        await create_db_and_tables()
        
        # Clear existing data
        await clear_database()
        
        # Test EAN scraping
        test_ean = "3596655503845"  # Example Celio EAN
        logger.info(f"Testing scraping for EAN: {test_ean}")
        
        result = await scraper_processor.process_ean(
            ean=test_ean,
            brand="CELIO"
        )
        
        print("\nScraping Result:")
        print("-" * 50)
        for key, value in result.items():
            print(f"{key}: {value}")
            
    except Exception as e:
        logger.error(f"Error during test: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(test_scraper()) 