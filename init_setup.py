import os
import logging
from config.settings import settings

def init_directories():
    """Initialize required directories"""
    dirs = [
        'static',
        'static/uploads',
        'static/product_images',
        'templates'
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"Created directory: {dir_path}")

def init_env():
    """Create .env file if not exists"""
    if not os.path.exists('.env'):
        env_content = """DEBUG=True
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=sqlite:///ean_results.db
MAX_IMAGES_PER_PRODUCT=3"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        print("Created .env file")

if __name__ == "__main__":
    print("Initializing Scraper-MService...")
    init_directories()
    init_env()
    print("Initialization complete!") 