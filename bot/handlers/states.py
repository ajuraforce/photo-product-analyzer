"""
Finite State Machine states for conversation flow
"""
from aiogram.fsm.state import State, StatesGroup

class ProductStates(StatesGroup):
    """States for product processing workflow"""
    waiting_for_photo = State()
    waiting_for_price_confirmation = State() 
    waiting_for_manual_brand = State()
    waiting_for_admin_input = State()
    
class AdminStates(StatesGroup):
    """States for admin operations"""
    editing_product = State()
    setting_gender = State()
    setting_supplier = State()
    overriding_brand = State()
    bulk_operations = State()