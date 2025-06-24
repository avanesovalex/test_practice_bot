from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton,
                           ReplyKeyboardMarkup, KeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.database.repositories.admin import get_all_users, get_one_user


get_phone_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Отправить номер телефона📞', request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

menu_kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='Оставить заявку🗒'),
                KeyboardButton(text='Контакты📱')
            ],
            [KeyboardButton(text='Информация о компанииℹ')]
        ],
        resize_keyboard=True
    )

category_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Тех. проблема')],
            [KeyboardButton(text='Предложение')],
            [KeyboardButton(text='Вопрос'), KeyboardButton(text='Другое')],
            [KeyboardButton(text='Отменить')]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

send_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Отправить')],
            [KeyboardButton(text='Отменить')]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

async def get_tags_keyboard(selected_tags=None):
    if selected_tags is None:
        selected_tags = []
    
    tags = [
        "Ошибка оплаты",
        "Проблема с доступом",
        "Технический сбой", 
        "Вопрос по функционалу",
        "Баг в интерфейсе",
        "Другая проблема"
    ]

    buttons = []

    for i in range(0, len(tags), 3):
        row = []
        for tag in tags[i:i+3]:
            row.append(
                InlineKeyboardButton(
                    text=f'✅{tag}' if tag in selected_tags else tag,
                    callback_data=f'tag_{tag}'
                )
            )
        buttons.append(row)
    
    buttons.append([
        InlineKeyboardButton(text="➡️Продолжить", callback_data="continue_tags"),
        InlineKeyboardButton(text="❌Отменить", callback_data="cancel_tags")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

admin_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='📊Просмотреть статистику', callback_data='view_stats')],
        [InlineKeyboardButton(text='📧Отправить рассылку', callback_data='send_message')],
        [InlineKeyboardButton(text='👥Список пользователей', callback_data='users_page_0')]
    ]
)

back_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад в меню', callback_data='back_to_admin_menu')]
    ]
)

async def get_users_kb(page = 0, users_per_page = 5) -> InlineKeyboardBuilder:
    users = await get_all_users()
    total_pages = (len(users) + users_per_page - 1) // users_per_page
    
    builder = InlineKeyboardBuilder()
    
    # Добавляем кнопки пользователей
    for user in users[page*users_per_page : (page+1)*users_per_page]:
        user_data = await get_one_user(user)
        builder.button(
            text=f'👤{user_data[0]}', 
            callback_data=f"user_detail_{user}"
        )
    
    # Добавляем кнопки пагинации
    pagination_buttons = []
    if page > 0:
        pagination_buttons.append(
            ("⬅️", f"users_page_{page-1}")
        )
    if page < total_pages - 1:
        pagination_buttons.append(
            ("➡️", f"users_page_{page+1}")
        )
    
    if pagination_buttons:
        for text, callback_data in pagination_buttons:
            builder.button(text=text, callback_data=callback_data)
        builder.adjust(len(pagination_buttons))  # Размещаем кнопки пагинации в один ряд
    
    # Добавляем кнопку "В меню"
    builder.button(text="В меню", callback_data="back_to_admin_menu")
    
    # Все кнопки пользователей располагаем в столбец
    builder.adjust(1, 1, 1, 1, 1, 2 if (page > 0 and page < total_pages - 1) else 1, 1)
    
    return builder

async def get_user_kb(user_id):
    user_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='👤Профиль пользователя', url=f"tg://user?id={user_id}")],
            [InlineKeyboardButton(text='🔙Назад к списку', callback_data="users_page_0")]
        ]
    )
    return user_kb