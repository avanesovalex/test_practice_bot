from aiogram import Router, F
from aiogram.filters import or_f
from aiogram.types import (Message, InlineKeyboardMarkup, InlineKeyboardButton,
                           ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove)
from aiogram.fsm.context import FSMContext

from states import Menu, Request

router = Router()

@router.message(
    or_f(
        Request.wait_for_category,
        Request.wait_for_text,
        Request.wait_for_pic,
        Request.wait_for_send
    ),
    F.text.lower() == 'отменить')
async def cancel(message: Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Оставить заявку🗒')],
            [KeyboardButton(text='Контакты📱')],
            [KeyboardButton(text='Информация о компанииℹ')]
        ],
        resize_keyboard=True
    )

    await message.answer('Вы отменили заполнение заявки', reply_markup=keyboard)
    await state.set_state(Menu.in_menu)

@router.message(Menu.in_menu, F.text.lower() =='оставить заявку🗒')
async def get_request(message: Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Тех. проблема')],
            [KeyboardButton(text='Предложение')],
            [KeyboardButton(text='Вопрос'), KeyboardButton(text='Другое')],
            [KeyboardButton(text='Отменить')]
        ],
        resize_keyboard=True
    )
    await message.answer('Выберите категорию заявки', reply_markup=keyboard)
    await state.set_state(Request.wait_for_category)

@router.message(Request.wait_for_category)
async def get_category(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Отменить ')]
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
    photo_id = message.photo[-1].file_id # type: ignore
    user_data = await state.get_data()

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Отправить')],
            [KeyboardButton(text='Отменить')]
        ],
        resize_keyboard=True
    )
    
    req_msg = (
        f'Ваш скриншот прикреплен! Вот ваша заявка\n\n'
        f'Категория: {user_data['category']}\n'
        f'Текст заявки:\n{user_data['text']}'
    )

    await message.answer_photo(photo=photo_id, caption=f'{req_msg}', reply_markup=keyboard)
    await state.set_state(Request.wait_for_send)

@router.message(Request.wait_for_pic, F.text.lower() == 'продолжить без скриншота')
async def no_pic(message: Message, state: FSMContext):
    user_data = await state.get_data()

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Отправить')],
            [KeyboardButton(text='Отменить')]
        ],
        resize_keyboard=True
    )
    
    req_msg = (
        f'Вы продолжили без скриншота! Вот ваша заявка\n\n'
        f'Категория: {user_data['category']}\n'
        f'Текст заявки:\n{user_data['text']}'
    )

    await message.answer(f'{req_msg}', reply_markup=keyboard)
    await state.set_state(Request.wait_for_send)

@router.message(Request.wait_for_send, F.text.lower() == 'отправить')
async def send_request(message: Message, state: FSMContext):
    