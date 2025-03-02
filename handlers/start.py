from aiogram import Router, types
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
import time
from keyboards.all_keyboards import main_keyboard, inline_keyboard_for_approve
from states.bot_states import ProductSearch  # Убедитесь, что вы импортируете ProductSearch
from db_handler.main_handler import insertInUsers, addRequest, updateNameRequestByUserId, updateStageRequestByUserId
from datetime import datetime
from parsers.findRequiredItem import findRequiredItem, findReviewsOnMarketplaces
from gptRequests.gptRequests import gptRequest

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
        "madeAt": datetime.now(),
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
    await updateNameRequestByUserId(query, user_id)
    await updateStageRequestByUserId(2, user_id)
    await state.update_data(query=query, user_id=user_id)

    # Здесь обработайте запрос, например, ищите в базе данных
    #sent_message = await message.answer(f"Вы ищете товар: {query}")
    # time.sleep(1)
    #await sent_message.delete()
    #photo_url = "https://img.mvideo.ru/Big/20086721bb.jpg"
    #caption = "Пылесос ручной (handstick) Samsung Bespoke Jet Complete VS20A95823W жемчужный https://www.mvideo.ru/products/pylesos-ruchnoi-handstick-samsung-bespoke-jet-complete-vs20a95823w-zhemchuzhnyi-20086721?af_siteid=search_none&af_adset_id=5256438049&af_ad_id=14778726070&af_ad=---autotargeting&af_sub1=&af_sub2=3&idfa=&google_aid=&android_id=&oaid=&af_force_deeplink=true&utm_medium=cpc&utm_source=yandex&utm_campaign=cn:mg_dsa_feed_high-price_p_msk|cid:92626065&utm_term=---autotargeting&utm_content=ph:53131206633|re:53131206633|cid:92626065|gid:5256438049|aid:14778726070|adp:no|pos:premium3|src:search_none|dvc:desktop|coef_goal:22617267|region:213|%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0&pid=yandexdirect_int&c=mg_dsa_feed_high-price_p_msk&af_c_id=92626065&is_retargeting=true&af_reengagement_window=30d&af_click_lookback=7d&clickid=3696237440222363647&yclid=3696237440222363647"
    global approval
    caption, photo_url = findRequiredItem(query)
    await state.update_data(url=caption)
    approval = await message.answer_photo(photo=photo_url,
                               caption="Это тот товар? \n" + caption,
                               reply_markup=inline_keyboard_for_approve()
                               )
    await updateStageRequestByUserId(3, message.from_user.id)
    # Завершаем состояние
    await state.set_state(ProductSearch.waiting_for_approval)

@start_router.callback_query(lambda callback_query: callback_query.data in ["yes", "no"])
async def process_callback(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("user_id")
    await updateStageRequestByUserId(4, user_id)
    await approval.delete()
    if callback_query.data == "yes":
        sent_message = await callback_query.message.answer("🔍 Поиск отзывов... 🔍")
        reviews = findReviewsOnMarketplaces(data.get("url"))
        responce = gptRequest(reviews=reviews)
        await sent_message.delete()
        await callback_query.message.answer(responce)
    elif callback_query.data == "no":
        await callback_query.message.answer("Повторите запрос точнее")
        await state.set_state(ProductSearch.waiting_for_query)
