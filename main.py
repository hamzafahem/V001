#from fastapi import FastAPI

#app = FastAPI()


#@app.get("/")
#async def root():
#    return {"message": "Hello World"}


#@app.get("/hello/{name}")
#async def say_hello(name: str):
#    return {"message": f"Hello {name}"}
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

from config.settings import settings
from api.routers import scraper_router, upload_router, export_router, health_router
#from api.error_handlers import setup_exception_handlers
from database.db_manager import create_db_and_tables

# Ensure directories exist
os.makedirs(settings.upload_folder, exist_ok=True)
os.makedirs(settings.image.storage_path, exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Service for scraping product information based on EAN codes",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup exception handlers
#setup_exception_handlers(app)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(scraper_router, prefix=settings.API_PREFIX)
app.include_router(upload_router, prefix=settings.API_PREFIX)
app.include_router(export_router, prefix=settings.API_PREFIX)
app.include_router(health_router, prefix=settings.API_PREFIX)

@app.on_event("startup")
async def on_startup():
    # Create database and tables
    await create_db_and_tables()

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "app_name": settings.APP_NAME}
    )

if __name__ == "__main__":
    # Ensure we're in the correct directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=settings.DEBUG)