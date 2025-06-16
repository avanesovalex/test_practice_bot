from aiogram import Router, F
from aiogram.filters import Command, or_f
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

from states import Admin, Menu
from database.repositories.admin import is_user_admin, get_all_users
from keyboards import admin_kb, send_kb, menu_kb

router = Router()

@router.message(
    or_f(
        Admin.wait_for_message,
        Admin.wait_for_send
    ),
    F.text.lower() == 'отменить')
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Вы отменили заполнение рассылки')
    await state.set_state(Menu.in_menu)

@router.message(Command('admin'))
async def admin_command(message: Message, state: FSMContext):
    if await is_user_admin(message.from_user.id): # type: ignore
        await message.answer('Выберите действие', reply_markup=admin_kb)
    else:
        await message.answer('У вас нет необходимых прав, чтобы воспользоваться данной командой')

@router.message(F.text.lower() == 'просмотреть статистику')
async def on_stats_btn(message: Message):
    await message.answer('Статистика вашего бота: test test test')

@router.message(F.text.lower() == 'отправить рассылку')
async def on_message_btn(message: Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Отменить')]
        ],
        resize_keyboard=True
    )
    await message.answer('Введите вашу рассылку:', reply_markup=keyboard)
    await state.set_state(Admin.wait_for_message)

@router.message(Admin.wait_for_message)
async def get_message(message: Message, state: FSMContext):
    await message.answer('Вот ваша рассылка:')
    if message.photo:
        await state.update_data(text = message.html_text if message.caption else '')
        await state.update_data(photo_id=message.photo[-1].file_id)
        
        data = await state.get_data()
        await message.answer_photo(data['photo_id'], data['text'], reply_markup=send_kb, parse_mode='html')
    else:
        await state.update_data(text = message.html_text)
        await state.update_data(photo_id=None)

        data = await state.get_data()
        await message.answer(data['text'], reply_markup=send_kb, parse_mode='html')

    await state.set_state(Admin.wait_for_send)

@router.message(Admin.wait_for_send, F.text.lower() == 'отправить')
async def send_message(message: Message, state: FSMContext):
    users = await get_all_users()
    data = await state.get_data()
    for user_id in users:
        if data['photo_id']:
            await message.bot.send_photo(user_id, data['photo_id'], caption=data['text'], parse_mode='html') # type: ignore
        else:
            await message.bot.send_message(user_id, data['text'], parse_mode='html') # type: ignore

    # Завершение
    await state.clear()
    await message.answer(
        f'✅ Рассылка отправлена!\n\nСтолько людей получили рассылку: {len(users)}',
        reply_markup=menu_kb
    )
    await state.set_state(Menu.in_menu)