import re
import datetime

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from states import Registration, Menu
from keyboards import get_phone_kb, menu_kb
from database.repositories.user import add_user

router = Router()

@router.message(Command('start'))
async def on_start(message: Message, state: FSMContext):
    await message.answer('Добро пожаловать!\n\nЧтобы начать пользоваться нашим ботом, пройдите небольшую регистрацию🗒\n\nВведите ваше ФИО:', reply_markup=ReplyKeyboardRemove())
    await state.set_state(Registration.wait_for_name)

@router.message(Registration.wait_for_name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Отлично! Теперь введите вашу дату рождения в формате ДД.ММ.ГГГГ (например: 06.02.2001):')
    await state.set_state(Registration.wait_for_birthdate)

@router.message(Registration.wait_for_birthdate)
async def get_birthdate(message: Message, state: FSMContext):
    date_pattern = r'^\d{2}\.\d{2}\.\d{4}$'

    if not re.match(date_pattern, message.text): # type: ignore
        await message.answer('Неверный формат даты. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ:')
        return
    
    try:
        day, month, year = map(int, message.text.split('.')) # type: ignore
        birthdate = datetime.datetime(year, month, day)
        
        if birthdate > datetime.datetime.now():
            await message.answer('Дата рождения не может быть в будущем. Пожалуйста, введите корректную дату:')
            return
        if year < 1900:
            await message.answer('Пожалуйста, введите реальный год рождения (не ранее 1900):')
            return
    except ValueError as e:
        await message.answer(f'Некорректная дата: {e}. Введите корректную дату:')
        return
    
    await state.update_data(birthdate=message.text)

    await message.answer('Последний шаг! Отправьте ваш номер телефона (в формате +7**********, либо нажав кнопку ниже):', reply_markup=get_phone_kb)
    await state.set_state(Registration.wait_for_phone)

@router.message(Registration.wait_for_phone, F.text.startswith('+7'))
async def wrong_phone(message: Message, state: FSMContext):
    if len(message.text) == 12: # type: ignore
        phone_number = message.text
        user_data = await state.get_data()
        await add_user(message.from_user.id, user_data['name'], # type: ignore
                    user_data['birthdate'], phone_number)


        await message.answer(f'Регистрация успешно завершена!\n\nФИО: {user_data['name']}\nДата рождения: {user_data['birthdate']}\nНомер телефона: {phone_number}', reply_markup=menu_kb)
        await state.set_state(Menu.in_menu)
    else:
        await message.answer('Пожалуйста, отправьте номер телефона в формате +7**********, либо используя кнопку ниже:')


@router.message(Registration.wait_for_phone, F.contact)
async def get_phone(message: Message, state: FSMContext):
    phone_number = message.contact.phone_number # type: ignore
    user_data = await state.get_data()
    await add_user(message.from_user.id, user_data['name'], # type: ignore
                   user_data['birthdate'], phone_number)


    await message.answer(f'Регистрация успешно завершена!\n\nФИО: {user_data['name']}\nДата рождения: {user_data['birthdate']}\nНомер телефона: {phone_number}', reply_markup=menu_kb)
    await state.set_state(Menu.in_menu)

@router.message(Registration.wait_for_phone)
async def get_phone_invalid(message: Message):
    await message.answer('Пожалуйста, отправьте номер телефона в формате +7**********, либо используя кнопку ниже:')
