from aiogram.filters.state import State, StatesGroup

class ProductSearch(StatesGroup):
    waiting_for_query = State()
    waiting_for_approval = State()