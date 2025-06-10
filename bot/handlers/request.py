from aiogram import Router, F
from aiogram.filters import or_f
from aiogram.types import (Message, CallbackQuery,
                           ReplyKeyboardMarkup, KeyboardButton)
from aiogram.fsm.context import FSMContext

from states import Menu, Request
from keyboards import menu_kb, category_kb, send_kb, get_priority_keyboard
from config import PRIORITIES, ADMIN_CHAT_ID
from database.repositories.requests import add_request, get_request

router = Router()

@router.message(
    or_f(
        Request.wait_for_category,
        Request.wait_for_text,
        Request.wait_for_pic,
        Request.wait_for_priority,
        Request.wait_for_send
    ),
    F.text.lower() == 'отменить')
async def cancel(message: Message, state: FSMContext):

    await message.answer('Вы отменили заполнение заявки', reply_markup=menu_kb)
    await state.set_state(Menu.in_menu)

@router.message(Menu.in_menu, F.text.lower() =='оставить заявку🗒')
async def new_request(message: Message, state: FSMContext):
    await message.answer('Выберите категорию заявки', reply_markup=category_kb)
    await state.set_state(Request.wait_for_category)

@router.message(Request.wait_for_category)
async def get_category(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Отменить')]
        ],
        resize_keyboard=True
    )

    await message.answer('Введите текст заявки', reply_markup=keyboard)
    await state.set_state(Request.wait_for_text)

@router.message(Request.wait_for_text)
async def get_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Продолжить без скриншота')],
            [KeyboardButton(text='Отменить')]
        ],
        resize_keyboard=True
    )
    
    await message.answer('Прикрепите скриншот', reply_markup=keyboard)
    await state.set_state(Request.wait_for_pic)

@router.message(Request.wait_for_pic, F.photo)
async def get_pic(message: Message, state: FSMContext):
    global attached_photo
    attached_photo = True
    await state.update_data(photo_id=message.photo[-1].file_id) # type: ignore

    await message.answer('Ваш скриншот удачно прикреплен\nВыберите срочность обработки заявки',
                         reply_markup=get_priority_keyboard())
    await state.set_state(Request.wait_for_priority)

@router.message(Request.wait_for_pic, F.text.lower() == 'продолжить без скриншота')
async def no_pic(message: Message, state: FSMContext):
    global attached_photo
    attached_photo = False
    await message.answer('Вы решили продолжить без скриншота\nВыберите срочность обработки заявки',
                         reply_markup=get_priority_keyboard())
    await state.set_state(Request.wait_for_priority)

@router.callback_query(Request.wait_for_priority, F.data.startswith("priority_"))
async def handle_priority(callback: CallbackQuery, state: FSMContext):
    selected_priority = callback.data.split("_")[1] # type: ignore
    await state.update_data(priority=selected_priority)
    
    await callback.message.edit_reply_markup( # type: ignore
        reply_markup=get_priority_keyboard(selected_priority)
    )
    await callback.answer()

@router.callback_query(Request.wait_for_priority, F.data == "continue_priority")
async def handle_continue(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    priority = user_data.get("priority", "normal")
    await state.update_data(priority=priority)
    
    await callback.message.answer('✅Готово! Вот ваша заявка') # type: ignore

    req_msg = (
        f'Приоритет: {PRIORITIES[priority]}\n'
        f'Категория: {user_data['category']}\n'
        f'Текст заявки:\n{user_data['text']}'
    )

    if attached_photo:
        await callback.message.answer_photo(user_data['photo_id'], f'{req_msg}', reply_markup=send_kb) # type: ignore
    else:
        await callback.message.answer(f'{req_msg}', reply_markup=send_kb) # type: ignore
    await state.set_state(Request.wait_for_send)

@router.message(Request.wait_for_send, F.text.lower() == 'отправить')
async def send_request(message: Message, state: FSMContext):
    user_data = await state.get_data()
    global attached_photo
    if attached_photo:
        request_id = await add_request(message.from_user.id, user_data['category'], # type: ignore
                          user_data['text'], user_data['photo_id'])
    else:
        request_id = await add_request(message.from_user.id, user_data['category'], user_data['text']) # type: ignore

    request = await get_request(request_id)
    request_msg = (
        f"📌 Номер заявки: {request['id']}\n"
        f"👤 Пользователь: {request['full_name']}\n"
        f"📞 Телефон: {request['phone_number']}\n"
        f"🏷 Категория: {request['category']}\n"
        f"🔢 Приоритет: {PRIORITIES[user_data.get('priority', 'normal')]}\n"
        f"📝 Текст заявки:\n{request['request_text']}\n"
    )

    if request.get('photo_id'):
        await message.bot.send_photo(ADMIN_CHAT_ID, request['photo_id'], caption=request_msg) # type: ignore
    else:
        await message.bot.send_message(ADMIN_CHAT_ID, request_msg) # type: ignore

    await message.answer('Ваша заявка успешно отправлена в поддержку! Ожидайте ответа', reply_markup=menu_kb)
    await state.set_state(Menu.in_menu)