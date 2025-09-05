#!/usr/bin/env python3
"""
Simple bot runner for testing
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

async def run_bot():
    """Run the bot with basic configuration"""
    try:
        from bot.main import main
        await main()
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please ensure all dependencies are installed: pip install -r requirements.txt")
    except Exception as e:
        print(f"Bot error: {e}")

if __name__ == "__main__":
    print("🤖 Starting Telegram Product Cataloger Bot...")
    
    # Check for minimal configuration
    if not os.getenv("BOT_TOKEN"):
        print("⚠️  Warning: BOT_TOKEN not set")
        print("Set your Telegram bot token: export BOT_TOKEN='your_bot_token'")
    
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\n✅ Bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")