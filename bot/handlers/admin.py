from aiogram import Router, F
from aiogram.filters import Command, or_f
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

from states import Admin, Menu
from database.repositories.admin import is_user_admin, get_all_users
from keyboards import send_kb, menu_kb

router = Router()

@router.message(
    or_f(
        Admin.wait_for_text,
        Admin.wait_for_pic,
        Admin.wait_for_send
    ),
    F.text.lower() == 'отменить')
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Вы отменили заполнение рассылки')
    await state.set_state(Menu.in_menu)

@router.message(Command('admin'))
async def on_admin_cmd(message: Message, state: FSMContext):
    if await is_user_admin(message.from_user.id): # type: ignore
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text='Отменить')]
            ],
            resize_keyboard=True
        )
        await message.answer('Введите текст рассылки:', reply_markup=keyboard)
        await state.set_state(Admin.wait_for_text)
    else:
        await message.answer('У вас нет необходимых прав, чтобы воспользоваться данной командой')

@router.message(Admin.wait_for_text)
async def get_text(message: Message, state: FSMContext):
    await state.update_data(text=message.html_text)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Продолжить без фото')],
            [KeyboardButton(text='Отменить')]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await message.answer('Прикрепите фото', reply_markup=keyboard)
    await state.set_state(Admin.wait_for_pic)

@router.message(Admin.wait_for_pic, F.photo)
async def get_pic(message: Message, state: FSMContext):
    global attached_photo
    attached_photo = True

    await state.update_data(photo_id=message.photo[-1].file_id) # type: ignore
    data = await state.get_data()

    await message.answer('Ваше фото успешно прикреплено\nВот ваша рассылка:')
    await message.answer_photo(data['photo_id'], data['text'], reply_markup=send_kb, parse_mode='html')
    await state.set_state(Admin.wait_for_send)

@router.message(Admin.wait_for_pic, F.text.lower() == 'продолжить без фото')
async def no_pic(message: Message, state: FSMContext):
    global attached_photo
    attached_photo = False

    data = await state.get_data()

    await message.answer('Вы решили продолжить без фото\nВот ваша рассылка:')
    await message.answer(data['text'], reply_markup=send_kb, parse_mode='html')
    await state.set_state(Admin.wait_for_send)

@router.message(Admin.wait_for_send, F.text.lower() == 'отправить')
async def send_message(message: Message, state: FSMContext):
    global attached_photo
    users = await get_all_users()
    data = await state.get_data()
    for user_id in users: # type: ignore
        if attached_photo:
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