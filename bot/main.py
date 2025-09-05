"""
Main Telegram bot application
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
try:
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode
except ImportError:
    # Fallback for different aiogram versions
    DefaultBotProperties = None
    ParseMode = None

from bot.config import Config
from bot.handlers import start, photo, admin

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main bot function"""
    # Check if bot token is configured
    if not Config.BOT_TOKEN:
        logger.error("BOT_TOKEN not configured. Please set the environment variable.")
        return
    
    # Initialize bot and dispatcher
    if DefaultBotProperties and ParseMode:
        bot = Bot(
            token=Config.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
        )
    else:
        # Fallback for older aiogram versions
        bot = Bot(token=Config.BOT_TOKEN)
    
    # Use memory storage for FSM
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Include routers
    dp.include_router(start.router)
    dp.include_router(photo.router)
    dp.include_router(admin.router)
    
    # Test bot token
    try:
        bot_info = await bot.get_me()
        logger.info(f"Bot initialized: @{bot_info.username}")
    except Exception as e:
        logger.error(f"Failed to initialize bot: {e}")
        return
    
    # Start polling
    logger.info("Starting bot polling...")
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application stopped")