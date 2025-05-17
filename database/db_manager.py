from databases import Database
import logging
import asyncio
from config.settings import settings

logger = logging.getLogger(__name__)

# Database instance
database = Database(settings.DATABASE_URL)  # Maintenant, on utilise DATABASE_URL

async def create_db_and_tables():
    """Create database and tables if they don't exist"""
    logger.info("Initializing database and tables")
    
    try:
        if not database.is_connected:
            await database.connect()

        # Create products table
        await database.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ean TEXT NOT NULL UNIQUE,
                brand TEXT,
                category TEXT,
                name TEXT,
                description TEXT,
                color TEXT,
                size TEXT,
                long_description TEXT,
                source TEXT,
                source_url TEXT,
                price TEXT,
                box_number TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create product_images table
        await database.execute('''
            CREATE TABLE IF NOT EXISTS product_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_ean TEXT NOT NULL,
                image_url TEXT,
                local_path TEXT,
                is_primary BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_ean) REFERENCES products(ean) ON DELETE CASCADE
            )
        ''')
        
        # Create indexes
        await database.execute('''
            CREATE INDEX IF NOT EXISTS idx_ean ON products(ean)
        ''')
        
        await database.execute('''
            CREATE INDEX IF NOT EXISTS idx_brand ON products(brand)
        ''')
        
        logger.info("Database initialization complete")
        
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        raise

async def close_db_connection():
    """Close database connection"""
    if database.is_connected:
        await database.disconnect()