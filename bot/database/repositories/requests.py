from database.db import db

async def add_request(user_id, category, request_text, photo_id=None):
    await db.execute(
        '''INSERT INTO requests(user_id, category, request_text, photo_id) VALUES($1, $2, $3, $4)''',
        user_id, category, request_text, photo_id
    )