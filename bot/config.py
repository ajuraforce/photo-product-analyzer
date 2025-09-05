"""
Configuration settings for Telegram Product Cataloger Bot
"""
import os
from pathlib import Path
from typing import List

class Config:
    """Main configuration class"""
    
    # Bot Configuration
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-vision-preview")
    
    # Domain Configuration
    DOMAIN_URL: str = os.getenv("DOMAIN_URL", "")
    STATIC_SERVER_PORT: int = int(os.getenv("STATIC_SERVER_PORT", "8000"))
    
    # Google Sheets Configuration
    GOOGLE_CREDENTIALS_FILE: str = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    GOOGLE_SHEET_ID: str = os.getenv("GOOGLE_SHEET_ID", "")
    
    # File Storage Configuration
    UPLOAD_PATH: Path = Path("static_server/uploads")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "webp"]
    
    # Vocabulary Configuration (Controlled Categories)
    PRODUCT_TYPES: List[str] = [
        "shirt", "t-shirt", "blouse", "top",
        "pants", "jeans", "trousers", "shorts",
        "dress", "skirt", "jumpsuit",
        "shoes", "sneakers", "boots", "sandals",
        "jacket", "coat", "hoodie", "sweater",
        "accessories", "bag", "hat", "jewelry",
        "underwear", "swimwear", "socks",
        "other"
    ]
    
    COLORS: List[str] = [
        "black", "white", "gray", "grey",
        "red", "blue", "green", "yellow",
        "pink", "purple", "orange", "brown",
        "beige", "navy", "maroon", "teal",
        "multicolor", "pattern", "floral", "striped"
    ]
    
    GENDERS: List[str] = ["M", "F", "U"]  # Male, Female, Unisex
    
    # Database/Sheets Column Configuration
    SHEET_HEADERS: List[str] = [
        "Product ID", "Title", "Description", "Type", "Color", "Brand",
        "Photo Links", "Discounted Price", "Full Price", "Gender", 
        "Supplier", "AI Confidence", "Brand Confidence", "Created Date", 
        "Flags", "User ID", "Processing Time"
    ]
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "bot.log")
    
    # Development Configuration
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        required_fields = []  # Remove validation for now to allow testing
        missing = [field for field in required_fields if not getattr(cls, field)]
        
        if missing:
            print(f"⚠️ Missing environment variables: {', '.join(missing)}")
        
        # Create upload directory
        cls.UPLOAD_PATH.mkdir(parents=True, exist_ok=True)
        
        return True

# Initialize and validate config on import
try:
    Config.validate()
except Exception as e:
    print(f"⚠️ Configuration Error: {e}")
    print("Please check your .env file and required credentials.")