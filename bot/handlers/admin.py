"""
Admin command handlers
"""
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.handlers.states import AdminStates

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("gender"))
async def set_gender_command(message: Message, state: FSMContext):
    """Handle /gender command"""
    args = message.text.split()[1:] if message.text else []
    
    if not args or args[0].upper() not in ['M', 'F', 'U']:
        await message.answer(
            "Usage: `/gender M|F|U`\n"
            "• M = Male\n"
            "• F = Female\n"
            "• U = Unisex",
            parse_mode="Markdown"
        )
        return
    
    gender = args[0].upper()
    await state.update_data(default_gender=gender)
    
    gender_names = {'M': 'Male', 'F': 'Female', 'U': 'Unisex'}
    await message.answer(f"✅ Default gender set to: {gender_names[gender]}")

@router.message(Command("supplier"))
async def set_supplier_command(message: Message, state: FSMContext):
    """Handle /supplier command"""
    args = message.text.split(maxsplit=1)[1:] if message.text else []
    
    if not args:
        await message.answer(
            "Usage: `/supplier <supplier_name>`\n"
            "Example: `/supplier Nike Store`",
            parse_mode="Markdown"
        )
        return
    
    supplier = args[0]
    await state.update_data(default_supplier=supplier)
    await message.answer(f"✅ Default supplier set to: {supplier}")

@router.message(Command("brand"))
async def override_brand_command(message: Message, state: FSMContext):
    """Handle /brand command"""
    args = message.text.split(maxsplit=1)[1:] if message.text else []
    
    if not args:
        await message.answer(
            "Usage: `/brand <brand_name>`\n"
            "Example: `/brand Nike`\n"
            "Use this to override AI brand detection.",
            parse_mode="Markdown"
        )
        return
    
    brand = args[0]
    await state.update_data(brand_override=brand)
    await message.answer(f"✅ Brand override set to: {brand}\nThis will be used for the next product.")

@router.message(Command("edit_price"))
async def edit_price_command(message: Message, state: FSMContext):
    """Handle /edit_price command"""
    args = message.text.split()[1:] if message.text else []
    
    if len(args) not in [1, 2]:
        await message.answer(
            "Usage: `/edit_price <price>` or `/edit_price <discounted> <full>`\n"
            "Examples:\n"
            "• `/edit_price 29.99`\n"
            "• `/edit_price 24.99 29.99`",
            parse_mode="Markdown"
        )
        return
    
    try:
        if len(args) == 1:
            price = float(args[0])
            await state.update_data(price_override={'discounted': price, 'full': price})
            await message.answer(f"✅ Price override set to: ${price}")
        else:
            discounted = float(args[0])
            full = float(args[1])
            await state.update_data(price_override={'discounted': discounted, 'full': full})
            await message.answer(f"✅ Price override set to: ${discounted} (was ${full})")
            
    except ValueError:
        await message.answer("❌ Invalid price format. Please use numbers only.")

@router.message(Command("clear"))
async def clear_overrides_command(message: Message, state: FSMContext):
    """Handle /clear command"""
    await state.clear()
    await message.answer("✅ All overrides and settings cleared.")

@router.message(Command("settings"))
async def show_settings_command(message: Message, state: FSMContext):
    """Handle /settings command"""
    data = await state.get_data()
    
    settings_msg = "⚙️ **Current Settings:**\n\n"
    
    if data.get('default_gender'):
        gender_names = {'M': 'Male', 'F': 'Female', 'U': 'Unisex'}
        settings_msg += f"👤 **Gender**: {gender_names[data['default_gender']]}\n"
    
    if data.get('default_supplier'):
        settings_msg += f"🏪 **Supplier**: {data['default_supplier']}\n"
    
    if data.get('brand_override'):
        settings_msg += f"🏢 **Brand Override**: {data['brand_override']}\n"
    
    if data.get('price_override'):
        price_data = data['price_override']
        if price_data['discounted'] == price_data['full']:
            settings_msg += f"💰 **Price Override**: ${price_data['full']}\n"
        else:
            settings_msg += f"💰 **Price Override**: ${price_data['discounted']} (was ${price_data['full']})\n"
    
    if len(settings_msg) == len("⚙️ **Current Settings:**\n\n"):
        settings_msg += "No custom settings configured.\n"
    
    settings_msg += "\nUse `/clear` to reset all settings."
    
    await message.answer(settings_msg, parse_mode="Markdown")