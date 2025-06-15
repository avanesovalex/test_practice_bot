from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton,
                           ReplyKeyboardMarkup, KeyboardButton)

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
        resize_keyboard=True
    )

send_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Отправить')],
            [KeyboardButton(text='Отменить')]
        ],
        resize_keyboard=True
    )

def get_tags_keyboard(selected_tags=None):
    """Создаёт клавиатуру с выбором тегов."""
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
    
    buttons = [
        [
            InlineKeyboardButton(
                text=f"✅{tags[0]}" if tags[0] in selected_tags else tags[0],
                callback_data=f"tag_{tags[0]}"
            ),
            InlineKeyboardButton(
                text=f"✅{tags[1]}" if tags[1] in selected_tags else tags[1],
                callback_data=f"tag_{tags[1]}"
            ),
            InlineKeyboardButton(
                text=f"✅{tags[2]}" if tags[2] in selected_tags else tags[2],
                callback_data=f"tag_{tags[2]}"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"✅{tags[3]}" if tags[3] in selected_tags else tags[3],
                callback_data=f"tag_{tags[3]}"
            ),
            InlineKeyboardButton(
                text=f"✅{tags[4]}" if tags[4] in selected_tags else tags[4],
                callback_data=f"tag_{tags[4]}"
            ),
            InlineKeyboardButton(
                text=f"✅{tags[5]}" if tags[5] in selected_tags else tags[5],
                callback_data=f"tag_{tags[5]}"
            )
        ],
        [
            InlineKeyboardButton(
                text="➡️Продолжить",
                callback_data="continue_tags"
            ),
            InlineKeyboardButton(
                text="❌Отменить",
                callback_data="cancel_tags"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)