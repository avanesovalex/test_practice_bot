from database.db import db


async def add_user(user_id, full_name, birth_date, phone_number):
    await db.execute(
        '''INSERT INTO users(user_id, full_name, birth_date, phone_number) VALUES($1, $2, $3, $4)
        ON CONFLICT (user_id) DO NOTHING''',
        user_id, full_name, birth_date, phone_number
    )


async def update_last_activity(user_id):
    await db.execute(
        '''UPDATE users SET last_activity = CURRENT_TIMESTAMP WHERE user_id = $1;''', user_id
    )