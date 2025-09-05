"""
Google Sheets integration for product data storage
"""
import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

import gspread_asyncio
from google.oauth2.service_account import Credentials
from google.auth.exceptions import RefreshError

from bot.config import Config

logger = logging.getLogger(__name__)

class GoogleSheetsManager:
    """Google Sheets integration for storing product data"""
    
    def __init__(self):
        self.credentials_file = Config.GOOGLE_CREDENTIALS_FILE
        self.sheet_id = Config.GOOGLE_SHEET_ID
        self.headers = Config.SHEET_HEADERS
        self._agcm: Optional[gspread_asyncio.AsyncioGspreadClientManager] = None
        self._initialized = False
        
    def get_creds(self):
        """Get Google credentials for asyncio gspread client"""
        try:
            creds = Credentials.from_service_account_file(self.credentials_file)
            scoped = creds.with_scopes([
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive",
            ])
            return scoped
        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")
            return None

    async def initialize(self):
        """Initialize the Google Sheets client"""
        try:
            if not self.credentials_file or not self.sheet_id:
                logger.warning("Google Sheets not configured - credentials or sheet ID missing")
                return False
                
            self._agcm = gspread_asyncio.AsyncioGspreadClientManager(self.get_creds)
            self._initialized = True
            logger.info("Google Sheets client initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets: {e}")
            return False

    async def add_product_row(self, product_data: Dict[str, Any]) -> bool:
        """
        Add a new product row to Google Sheets
        
        Args:
            product_data: Dictionary containing product information
            
        Returns:
            True if successful, False otherwise
        """
        if not self._initialized:
            if not await self.initialize():
                return False
        
        try:
            agc = await self._agcm.authorize()
            sheet = await agc.open_by_key(self.sheet_id)
            worksheet = await sheet.get_sheet1()  # Use first worksheet

            # Prepare row data in the expected column order
            row_data = [
                product_data.get('product_id', ''),
                product_data.get('title', ''),
                product_data.get('description', ''),
                product_data.get('type', ''),
                product_data.get('color', ''),
                product_data.get('brand', ''),
                product_data.get('photo_links', ''),
                product_data.get('discounted_price', ''),
                product_data.get('full_price', ''),
                product_data.get('gender', 'U'),
                product_data.get('supplier', ''),
                product_data.get('ai_confidence', ''),
                product_data.get('brand_confidence', ''),
                product_data.get('created_date', ''),
                product_data.get('flags', ''),
                product_data.get('user_id', ''),
                product_data.get('processing_time', '')
            ]

            await worksheet.append_row(row_data)
            logger.info(f"Added product {product_data.get('product_id')} to sheet")
            return True

        except Exception as e:
            logger.error(f"Failed to add row to sheet: {e}")
            return False

    async def setup_sheet_headers(self):
        """Setup column headers if sheet is empty"""
        if not self._initialized:
            if not await self.initialize():
                return False
                
        try:
            agc = await self._agcm.authorize()
            sheet = await agc.open_by_key(self.sheet_id)
            worksheet = await sheet.get_sheet1()

            # Check if headers exist
            values = await worksheet.get_all_values()
            if not values or (len(values) == 1 and not any(values[0])):
                await worksheet.clear()
                await worksheet.append_row(self.headers)
                logger.info("Sheet headers created")
                return True
            else:
                logger.info("Sheet headers already exist")
                return True

        except Exception as e:
            logger.error(f"Failed to setup sheet headers: {e}")
            return False
    
    async def get_products_count(self) -> int:
        """Get total number of products in the sheet"""
        if not self._initialized:
            if not await self.initialize():
                return 0
                
        try:
            agc = await self._agcm.authorize()
            sheet = await agc.open_by_key(self.sheet_id)
            worksheet = await sheet.get_sheet1()
            
            values = await worksheet.get_all_values()
            # Subtract 1 for headers
            return max(0, len(values) - 1)
            
        except Exception as e:
            logger.error(f"Failed to get products count: {e}")
            return 0
    
    async def test_connection(self) -> bool:
        """Test Google Sheets connection"""
        if not self._initialized:
            if not await self.initialize():
                return False
                
        try:
            agc = await self._agcm.authorize()
            sheet = await agc.open_by_key(self.sheet_id)
            await sheet.get_sheet1()
            logger.info("Google Sheets connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"Google Sheets connection test failed: {e}")
            return False