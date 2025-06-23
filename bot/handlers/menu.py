from aiogram import Router, F
from aiogram.types import (Message, InlineKeyboardMarkup, InlineKeyboardButton)

from files.states import Menu


router = Router()


@router.message(Menu.in_menu, F.text.lower() =='контакты📱')
async def get_contacts(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Наш сайт🌐', url='example.com')]
        ]
    )

    contact_text = (
        'Контакты 📞✉️\n\n'
        '☎️ Телефон: +7 (123) 456-78-90\n'
        '📧 Email: info@company.ru\n\n'
        '📍 Адрес: г. Москва, ул. Мира, 1'
    )

    await message.answer(text=contact_text, reply_markup=keyboard)


@router.message(Menu.in_menu, F.text.lower() =='информация о компанииℹ')
async def get_info(message: Message):
    info_text = (
        'Мы - КОМПАНИЯ, диамично развивающаяся компания, которая создает будущее уже сегодня! 🚀\n\n'
        '🔹 Год основания: 2015\n'
        '🔹 Сфера деятельности: IT-решения, цифровые инновации и консалтинг\n'
        '🔹 Миссия: Превращать сложные задачи в простые и элегантные решения 💡\n\n'
        'Наши ценности:\n'
        '✅ Качество — мы стремимся к совершенству в каждом проекте\n'
        '✅ Клиентоориентированность — ваш успех = наш успех 🤝\n'
        '✅ Инновации — смелые идеи и передовые технологии\n\n'
        'КОМПАНИЯ — там, где рождается прогресс! 💻🔧'
    )

    await message.answer_photo(photo='https://static.tildacdn.com/tild6161-6337-4836-a334-303336316433/0025-025-Kruche-nas-.jpg', caption=info_text)