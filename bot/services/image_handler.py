"""
Image download, validation, and storage service
"""
import aiofiles
import aiohttp
import uuid
import logging
from pathlib import Path
from typing import List, Tuple, Optional
from PIL import Image
import io

from aiogram import Bot
from aiogram.types import PhotoSize

from bot.config import Config

logger = logging.getLogger(__name__)

class ImageHandler:
    """Handles image download, validation, and storage"""
    
    def __init__(self):
        self.upload_path = Config.UPLOAD_PATH
        self.domain_url = Config.DOMAIN_URL
        self.max_file_size = Config.MAX_FILE_SIZE
        self.allowed_extensions = Config.ALLOWED_EXTENSIONS
        
        # Ensure upload directory exists
        self.upload_path.mkdir(parents=True, exist_ok=True)
    
    async def download_and_store_photo(self, bot: Bot, photos: List[PhotoSize]) -> Tuple[str, str]:
        """
        Download the highest quality photo from Telegram and store locally
        
        Args:
            bot: Telegram bot instance
            photos: List of photo sizes from Telegram
            
        Returns:
            Tuple of (local_file_path, public_url)
        """
        try:
            # Get highest quality photo (largest file_size)
            largest_photo = max(photos, key=lambda p: p.file_size or 0)
            
            # Check file size limit
            if largest_photo.file_size and largest_photo.file_size > self.max_file_size:
                raise ValueError(f"File size {largest_photo.file_size} exceeds limit {self.max_file_size}")
            
            # Get file info from Telegram
            file = await bot.get_file(largest_photo.file_id)
            
            # Generate unique filename
            file_extension = Path(file.file_path).suffix.lower() or '.jpg'
            if file_extension.lstrip('.') not in self.allowed_extensions:
                file_extension = '.jpg'
                
            unique_filename = f"{uuid.uuid4().hex}{file_extension}"
            local_path = self.upload_path / unique_filename
            
            # Build Telegram file URL
            file_url = f"https://api.telegram.org/file/bot{bot.token}/{file.file_path}"
            
            # Download file
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as response:
                    if response.status == 200:
                        content = await response.read()
                        
                        # Save to local storage
                        async with aiofiles.open(local_path, 'wb') as f:
                            await f.write(content)
                            
                        logger.info(f"Image downloaded successfully: {unique_filename}")
                    else:
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status
                        )
            
            # Validate downloaded image
            if not await self.validate_image(local_path):
                # Clean up invalid file
                local_path.unlink(missing_ok=True)
                raise ValueError("Downloaded file is not a valid image")
            
            # Generate public URL
            public_url = f"{self.domain_url}/uploads/{unique_filename}"
            
            return str(local_path), public_url
            
        except Exception as e:
            logger.error(f"Failed to download and store photo: {e}")
            raise
    
    async def validate_image(self, file_path: Path) -> bool:
        """
        Validate that the file is a proper image
        
        Args:
            file_path: Path to the image file
            
        Returns:
            True if valid image, False otherwise
        """
        try:
            with Image.open(file_path) as img:
                # Verify image can be opened
                img.verify()
                
            # Reopen for additional checks (verify() invalidates the image)
            with Image.open(file_path) as img:
                # Check image dimensions (minimum size)
                if img.width < 100 or img.height < 100:
                    logger.warning(f"Image too small: {img.width}x{img.height}")
                    return False
                
                # Check if image has content
                if img.mode not in ['RGB', 'RGBA', 'L']:
                    logger.warning(f"Unsupported image mode: {img.mode}")
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Image validation failed: {e}")
            return False
    
    def cleanup_old_files(self, days_old: int = 30) -> int:
        """
        Clean up old uploaded files
        
        Args:
            days_old: Delete files older than this many days
            
        Returns:
            Number of files deleted
        """
        import time
        
        cutoff_time = time.time() - (days_old * 24 * 60 * 60)
        deleted_count = 0
        
        try:
            for file_path in self.upload_path.iterdir():
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    deleted_count += 1
                    
            logger.info(f"Cleaned up {deleted_count} old files")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            
        return deleted_count
    
    def get_file_info(self, filename: str) -> Optional[dict]:
        """
        Get information about an uploaded file
        
        Args:
            filename: Name of the file
            
        Returns:
            File information dict or None if file doesn't exist
        """
        file_path = self.upload_path / filename
        
        if not file_path.exists():
            return None
            
        try:
            stat = file_path.stat()
            
            # Get image dimensions if it's an image
            width, height = None, None
            try:
                with Image.open(file_path) as img:
                    width, height = img.size
            except:
                pass
                
            return {
                'filename': filename,
                'size': stat.st_size,
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'width': width,
                'height': height,
                'public_url': f"{self.domain_url}/uploads/{filename}"
            }
            
        except Exception as e:
            logger.error(f"Failed to get file info for {filename}: {e}")
            return None