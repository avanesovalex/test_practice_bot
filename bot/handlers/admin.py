from aiogram import Router, F
from aiogram.filters import Command, or_f
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from states import Admin
from database.repositories.admin import (is_user_admin, get_all_users, get_recently_active_users, 
                                         get_all_requests, get_recently_added_requests)
from keyboards import admin_kb, send_kb, back_kb

router = Router()

@router.message(
    or_f(
        Admin.wait_for_message,
        Admin.wait_for_send
    ),
    F.text.lower() == 'отменить')
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Вы отменили заполнение рассылки', reply_markup=ReplyKeyboardRemove())
    await message.answer('Выберите действие', reply_markup=admin_kb)

@router.message(Command('admin'))
async def admin_menu(message: Message, state: FSMContext):
    if await is_user_admin(message.from_user.id): # type: ignore
        await message.answer('Выберите действие', reply_markup=admin_kb)
    else:
        await message.answer('У вас нет необходимых прав, чтобы воспользоваться данной командой')

@router.callback_query(F.data == 'back_to_admin_menu')
async def back_to_admin(callback: CallbackQuery):
    await callback.message.delete() # type: ignore
    await callback.message.answer('Выберите действие', reply_markup=admin_kb) # type: ignore

@router.callback_query(F.data == 'view_stats')
async def on_stats_btn(callback: CallbackQuery):
    users = await get_all_users()
    recently_active_users = await get_recently_active_users()
    requests = await get_all_requests()
    recently_added_requests = await get_recently_added_requests()
    msg_text = (
        f'📊Статистика вашего бота:\n\n'
        f'👥Количество пользователей: {len(users)}\n'
        f'👥Активные пользователи (24 часа): {len(recently_active_users)}\n'
        f'📝Количество заявок (все время): {len(requests)}\n'
        f'📝Количество заявок (неделя): {len(recently_added_requests)}'
    )
    await callback.message.delete() # type: ignore
    await callback.message.answer(msg_text, reply_markup=back_kb) # type: ignore

@router.callback_query(F.data == 'send_message')
async def on_message_btn(callback: CallbackQuery, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Отменить')]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await callback.message.delete() # type: ignore
    await callback.message.answer('Введите вашу рассылку:', reply_markup=keyboard) # type: ignore
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
        f'✅ Рассылка отправлена!\n\nСтолько людей получили рассылку: {len(users)}'
    )
    await message.answer('Выберите действие', reply_markup=admin_kb)