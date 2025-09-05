#!/usr/bin/env python3
"""
Start script for the Telegram Product Cataloger Bot
"""
import asyncio
import multiprocessing
import time
import logging
from pathlib import Path
import sys
import os

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from bot.main import main
from static_server.server import app
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start_static_server():
    """Start the static file server"""
    try:
        logger.info("Starting static file server on port 8000...")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Static server error: {e}")

async def start_bot():
    """Start the Telegram bot"""
    try:
        logger.info("Starting Telegram bot...")
        await main()
    except Exception as e:
        logger.error(f"Bot error: {e}")

def run_bot():
    """Run bot in separate process"""
    asyncio.run(start_bot())

if __name__ == "__main__":
    logger.info("🚀 Starting Telegram Product Cataloger Bot")
    
    # Check if we have minimal configuration
    if not os.getenv("BOT_TOKEN"):
        logger.warning("⚠️  BOT_TOKEN not set - bot will not function properly")
    
    # Start static server in background process
    static_server_process = multiprocessing.Process(target=start_static_server)
    static_server_process.start()
    
    # Give server time to start
    time.sleep(2)
    
    try:
        # Start bot in main process
        run_bot()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        # Clean up
        static_server_process.terminate()
        static_server_process.join()
        logger.info("✅ Shutdown complete")