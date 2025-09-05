"""
Photo processing handlers
"""
import logging
import uuid
from datetime import datetime
from typing import Dict, Any

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.handlers.states import ProductStates
from bot.services.image_handler import ImageHandler
from bot.services.ai_vision import AIVisionAnalyzer
from bot.services.sheets import GoogleSheetsManager

logger = logging.getLogger(__name__)
router = Router()

# Initialize services
image_handler = ImageHandler()
ai_analyzer = AIVisionAnalyzer()
sheets_manager = GoogleSheetsManager()

@router.message(F.photo)
async def handle_photo(message: Message, state: FSMContext, bot):
    """Handle incoming product photos"""
    try:
        # Clear any existing state
        await state.clear()
        
        await message.answer("📸 Processing your photo... Please wait.")

        # Download and store image
        try:
            file_path, public_url = await image_handler.download_and_store_photo(
                bot, message.photo
            )
        except Exception as e:
            logger.error(f"Image download failed: {e}")
            await message.answer("❌ Failed to download image. Please try again with a different photo.")
            return

        # Analyze with AI Vision
        await message.answer("🤖 AI is analyzing the product...")
        ai_data = await ai_analyzer.analyze_product_image(public_url)

        # Generate product ID
        product_id = f"PROD_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"

        # Store data in state for later use
        product_data = {
            'product_id': product_id,
            'photo_path': file_path,
            'photo_url': public_url,
            'ai_data': ai_data,
            'created_date': datetime.now().isoformat(),
            'user_id': message.from_user.id,
            'user_name': message.from_user.full_name or "Unknown"
        }
        
        await state.update_data(product_data=product_data)

        # Show analysis results
        confidence_emoji = "🟢" if ai_data['confidence_score'] > 70 else "🟡" if ai_data['confidence_score'] > 40 else "🔴"
        brand_status = "✅" if ai_data['brand_confidence'] > 70 else "❓"

        analysis_msg = f"""
📊 **AI Analysis Results** {confidence_emoji}

🆔 **Product ID**: `{product_id}`
📝 **Title**: {ai_data['title']}
📖 **Description**: {ai_data['description']}
🏷️ **Type**: {ai_data['type']}
🎨 **Color**: {ai_data['color']}
🏢 **Brand**: {ai_data['brand']} {brand_status}

📈 **AI Confidence**: {ai_data['confidence_score']}%
🔗 **Photo**: [View Image]({public_url})

💰 **Next Step**: Please enter pricing information
📝 **Format**: `<discounted_price> <full_price>`
📝 **Example**: `29.99 39.99` or just `39.99` for single price

Type your pricing or `/skip` to save without pricing:
        """

        await message.answer(analysis_msg, parse_mode="Markdown")
        await state.set_state(ProductStates.waiting_for_price_confirmation)

    except Exception as e:
        logger.error(f"Error processing photo: {e}")
        await message.answer("❌ Error processing photo. Please try again.")

@router.message(ProductStates.waiting_for_price_confirmation)
async def handle_pricing(message: Message, state: FSMContext):
    """Handle pricing input"""
    try:
        user_data = await state.get_data()
        product_data = user_data.get('product_data')
        
        if not product_data:
            await message.answer("❌ Session expired. Please send a new photo.")
            await state.clear()
            return

        # Parse pricing
        discounted_price = ""
        full_price = ""
        
        if message.text and message.text.strip() != "/skip":
            prices = message.text.strip().split()
            if len(prices) == 1:
                # Single price
                try:
                    price = float(prices[0])
                    full_price = str(price)
                    discounted_price = str(price)
                except ValueError:
                    await message.answer("❌ Invalid price format. Please use numbers like `29.99` or `29.99 39.99`")
                    return
            elif len(prices) == 2:
                # Two prices
                try:
                    discounted_price = str(float(prices[0]))
                    full_price = str(float(prices[1]))
                except ValueError:
                    await message.answer("❌ Invalid price format. Please use numbers like `29.99 39.99`")
                    return
            else:
                await message.answer("❌ Invalid format. Use `<price>` or `<discounted> <full>` or `/skip`")
                return

        # Save to Google Sheets
        await message.answer("💾 Saving to Google Sheets...")
        
        # Prepare final product data
        ai_data = product_data['ai_data']
        final_data = {
            'product_id': product_data['product_id'],
            'title': ai_data['title'],
            'description': ai_data['description'],
            'type': ai_data['type'],
            'color': ai_data['color'],
            'brand': ai_data['brand'],
            'photo_links': product_data['photo_url'],
            'discounted_price': discounted_price,
            'full_price': full_price,
            'gender': 'U',  # Default to Unisex
            'supplier': '',
            'ai_confidence': ai_data['confidence_score'],
            'brand_confidence': ai_data['brand_confidence'],
            'created_date': product_data['created_date'],
            'flags': '',
            'user_id': product_data['user_id'],
            'processing_time': ai_data.get('processing_time', 0)
        }

        # Save to sheets
        success = await sheets_manager.add_product_row(final_data)
        
        if success:
            success_msg = f"""
✅ **Product Saved Successfully!**

🆔 **ID**: {product_data['product_id']}
💰 **Price**: {discounted_price if discounted_price else 'Not set'}
📊 **Status**: Added to catalog
🔗 **Photo**: [View]({product_data['photo_url']})

Ready for the next product! Send another photo 📸
            """
            await message.answer(success_msg, parse_mode="Markdown")
        else:
            await message.answer("⚠️ Product analyzed but failed to save to Google Sheets. Please check your configuration.")

        # Clear state
        await state.clear()

    except Exception as e:
        logger.error(f"Error handling pricing: {e}")
        await message.answer("❌ Error saving product. Please try again.")
        await state.clear()