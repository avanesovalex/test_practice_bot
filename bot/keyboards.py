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
            [KeyboardButton(text='Оставить заявку🗒')],
            [KeyboardButton(text='Контакты📱')],
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

def get_priority_keyboard(selected_priority = 'normal'):
    """Создаёт клавиатуру с выбором приоритета."""
    buttons = [
        [
            InlineKeyboardButton(
                text=f"✅🔴Срочно" if selected_priority == "urgent" else "🔴Срочно",
                callback_data="priority_urgent"
            ),
            InlineKeyboardButton(
                text=f"✅🟡Средне" if selected_priority == "normal" else "🟡Средне",
                callback_data="priority_normal"
            ),
            InlineKeyboardButton(
                text=f"✅🟢Несрочно" if selected_priority == "low" else "🟢Несрочно",
                callback_data="priority_low"
            )
        ],
        [
            InlineKeyboardButton(
                text="➡️Продолжить",
                callback_data="continue_priority"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)