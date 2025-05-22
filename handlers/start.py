from aiogram import Router, types
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
import time
from keyboards.all_keyboards import main_keyboard, inline_keyboard_for_approve
from states.bot_states import ProductSearch  # Убедитесь, что вы импортируете ProductSearch
from db_handler.main_handler import insertInUsers, addRequest, updateNameRequestByUserId, updateStageRequestByUserId, addResponse
from db_handler.database_manager import DatabaseManager
from decouple import config
from datetime import datetime
from parsers.findRequiredItem import findRequiredItem, findReviewsOnMarketplaces
from gptRequests.gptRequests import gptRequest
import json

auth_params = {
    'user': config('user'),
    'password': config('password'),
    'host': config('host'),
    'port': config('port'),
    'database': config('database')
}

start_router = Router()

@start_router.message(CommandStart())
async def cmd_start(message: types.Message):
    data = {
        "id": message.from_user.id,
        "name": str(message.from_user.full_name)
    }
    await insertInUsers(data)
    await message.answer("Добро пожаловать, воспользуйся меню для дальнейшей навигации!", reply_markup=main_keyboard(message.from_user.id))

# Обработчик нажатия кнопки "🔍 Найти товар"
@start_router.message(lambda message: message.text == "🔍 Найти товар")
async def find_product_start(message: types.Message, state: FSMContext):
    data = {
        "name": "",
        "madeat": datetime.now(),
        "success": False,
        "stage": 1,
        "user_id": message.from_user.id
    }
    await addRequest(data)
    await message.answer("Введите название товара для поиска:")
    await state.set_state(ProductSearch.waiting_for_query)

# Обработчик сообщения от пользователя с текстом запроса
@start_router.message(StateFilter(ProductSearch.waiting_for_query))
async def process_product_query(message: types.Message, state: FSMContext):
    query = message.text
    user_id = message.from_user.id
    print(f"Processing query from user {user_id}: {query}")  # Добавляем логирование
    
    await updateNameRequestByUserId(query, user_id)
    await updateStageRequestByUserId(2, user_id)
    await state.update_data(query=query, user_id=user_id)

    global approval
    try:
        caption, photo_url = findRequiredItem(query)
        if not caption or not photo_url:
            print(f"No product found for query: {query}")  # Добавляем логирование
            await message.answer("Не удалось найти товар. Пожалуйста, попробуйте другой запрос.")
            return

        print(f"Found product: {caption}")  # Добавляем логирование
        await state.update_data(url=caption)
        approval = await message.answer_photo(photo=photo_url,
                                   caption="Это тот товар? \n" + caption,
                                   reply_markup=inline_keyboard_for_approve()
                                   )
        await updateStageRequestByUserId(3, message.from_user.id)
        await state.set_state(ProductSearch.waiting_for_approval)
    except Exception as e:
        print(f"Error in process_product_query: {str(e)}")  # Добавляем логирование
        await message.answer("Произошла ошибка при поиске товара. Пожалуйста, попробуйте позже.")

@start_router.callback_query(lambda callback_query: callback_query.data in ["yes", "no"])
async def process_callback(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("user_id")
    user_query = data.get("query")
    print(f"Processing callback for user {user_id}, query: {user_query}")
    
    await updateStageRequestByUserId(4, user_id)
    await approval.delete()
    
    if callback_query.data == "yes":
        sent_message = await callback_query.message.answer("🔍 Поиск отзывов... 🔍")
        try:
            url = data.get("url")
            print(f"Searching reviews for URL: {url}")
            reviews = await findReviewsOnMarketplaces(url, user_query)
            print(f"Reviews search completed. Found {len(reviews) if reviews else 0} reviews")
            
            if not reviews:
                print("No reviews found")
                await sent_message.delete()
                await callback_query.message.answer("Не удалось найти отзывы для этого товара.")
                return
                
            print(f"Found {len(reviews)} reviews, analyzing...")
            item_title = user_query
            responce = await gptRequest(reviews=reviews, item_title=item_title)
            
            # Get the latest request ID for this user
            db_manager = DatabaseManager(**auth_params)
            async with db_manager as manager:
                query = """SELECT id FROM requests WHERE user_id = $1 ORDER BY madeat DESC LIMIT 1"""
                latest_request = await manager.fetch_data(query, user_id)
                if latest_request:
                    request_id = latest_request[0]['id']
                    # Save response to database
                    response_data = {
                        "request_id": request_id,
                        "user_id": user_id,
                        "ai_response": responce,
                        "marketplace_reviews": json.dumps(reviews)
                    }
                    await addResponse(response_data)
            
            await sent_message.delete()
            await callback_query.message.answer(responce)
        except Exception as e:
            print(f"Error in process_callback: {str(e)}")
            await sent_message.delete()
            await callback_query.message.answer("Произошла ошибка при поиске отзывов. Пожалуйста, попробуйте позже.")
    elif callback_query.data == "no":
        await callback_query.message.answer("Повторите запрос точнее")
        await state.set_state(ProductSearch.waiting_for_query)
