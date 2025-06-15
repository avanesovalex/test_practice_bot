from aiogram import Router, F
from aiogram.filters import or_f
from aiogram.types import (Message, CallbackQuery,
                           ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.fsm.context import FSMContext

from states import Menu, Request
from keyboards import menu_kb, category_kb, send_kb, get_tags_keyboard
from config import ADMIN_CHAT_ID
from database.repositories.requests import (add_request, add_request_tag, 
                                            get_request, get_request_tags)

router = Router()

@router.message(
    or_f(
        Request.wait_for_category,
        Request.wait_for_text,
        Request.wait_for_pic,
        Request.wait_for_tags,
        Request.wait_for_send
    ),
    F.text.lower() == 'отменить')
async def cancel(message: Message, state: FSMContext):
    await state.clear()
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
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await message.answer('Прикрепите скриншот', reply_markup=keyboard)
    await state.set_state(Request.wait_for_pic)

@router.message(Request.wait_for_pic, F.photo)
async def get_pic(message: Message, state: FSMContext):
    global attached_photo
    attached_photo = True
    await state.update_data(photo_id=message.photo[-1].file_id) # type: ignore

    await message.answer('Ваш скриншот удачно прикреплен\nВыберите теги к вашей заявке',
                         reply_markup=get_tags_keyboard())
    await state.set_state(Request.wait_for_tags)

@router.message(Request.wait_for_pic, F.text.lower() == 'продолжить без скриншота')
async def no_pic(message: Message, state: FSMContext):
    global attached_photo
    attached_photo = False
    await message.answer('Вы решили продолжить без скриншота\nВыберите теги к вашей заявке',
                         reply_markup=get_tags_keyboard())
    await state.set_state(Request.wait_for_tags)

@router.callback_query(Request.wait_for_tags, F.data.startswith("tag_"))
async def handle_tag_selection(callback: CallbackQuery, state: FSMContext):
    selected_tag = callback.data.split("_")[1]  # type: ignore
    user_data = await state.get_data()
    
    current_tags = user_data.get("tags", [])
    if selected_tag in current_tags:
        current_tags.remove(selected_tag)
    else:
        current_tags.append(selected_tag)
    
    await state.update_data(tags=current_tags)
    
    await callback.message.edit_reply_markup(  # type: ignore
        reply_markup=get_tags_keyboard(current_tags)
    )
    await callback.answer()

@router.callback_query(Request.wait_for_tags, F.data == "cancel_tags")
async def handle_tags_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete() # type: ignore
    await callback.message.answer('Вы отменили заполнение заявки', reply_markup=menu_kb) # type: ignore
    await state.set_state(Menu.in_menu)

@router.callback_query(Request.wait_for_tags, F.data == "continue_tags")
async def handle_continue(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    
    # Удаляем клавиатуру
    await callback.message.delete()  # type: ignore
    
    # Формируем сообщение с данными заявки
    req_msg = (
        f"Теги: {', '.join(user_data.get('tags', [])) or 'Не выбраны'}\n"
        f"Текст заявки:\n{user_data.get('text', '')}"
    )
    
    if user_data.get('photo_id'):
        await callback.message.answer_photo( # type: ignore
            user_data['photo_id'],
            caption=req_msg,
            reply_markup=send_kb
        )
    else:
        await callback.message.answer( # type: ignore
            req_msg,
            reply_markup=send_kb
        )
    
    await state.set_state(Request.wait_for_send)
    await callback.answer()

@router.message(Request.wait_for_send, F.text.lower() == 'отправить')
async def send_request(message: Message, state: FSMContext):
    user_data = await state.get_data()
    global attached_photo
    
    # Создаем базовую заявку
    if attached_photo:
        request_id = await add_request(
            user_id=message.from_user.id,  # type: ignore
            request_text=user_data['text'],
            photo_id=user_data['photo_id']
        )
    else:
        request_id = await add_request(
            user_id=message.from_user.id,  # type: ignore
            request_text=user_data['text']
        )
    
    # Добавляем теги по одному
    for tag in user_data.get('tags', []):
        await add_request_tag(request_id, tag)
    
    # Получаем данные для уведомления
    request = await get_request(request_id)
    print(request)
    tags = await get_request_tags(request_id)
    print(tags)
    
    # Формируем сообщение
    request_msg = (
        f"📌 Номер заявки: {request['id']}\n" # type: ignore
        f"👤 Пользователь: {request['full_name']}\n" # type: ignore
        f"📞 Телефон: {request['phone_number']}\n" # type: ignore
        f"🏷 Теги: {', '.join(tags) if tags else 'нет'}\n"
        f"📝 Текст:\n{request['request_text']}" # type: ignore
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👤 Профиль пользователя",
                    url=f"tg://user?id={message.from_user.id}" # type: ignore
                )
            ]
        ])
    
    # Отправка админу
    if request.get('photo_id'): # type: ignore
        await message.bot.send_photo(1217543203, request['photo_id'], caption=request_msg, reply_markup=keyboard)  # type: ignore
    else:
        await message.bot.send_message(1217543203, request_msg, reply_markup=keyboard)  # type: ignore
    
    # Завершение
    await state.clear()
    await message.answer(
        '✅ Заявка отправлена!',
        reply_markup=menu_kb
    )
    await state.set_state(Menu.in_menu)