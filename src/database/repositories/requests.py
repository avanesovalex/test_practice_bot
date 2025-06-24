from src.database.db import db


async def add_request(user_id, request_text, tags=None, photo_id=None):
    request_id = await db.fetchval(
        '''INSERT INTO requests(user_id, request_text, photo_id) 
        VALUES($1, $2, $3)
        RETURNING id''',
        user_id, request_text, photo_id
    )

    return request_id

 
async def add_request_tag(request_id, tag):
    await db.execute(
        '''INSERT INTO request_tags(request_id, tag) 
        VALUES($1, $2)
        ON CONFLICT (request_id, tag) DO NOTHING''',
        request_id, tag
    )

async def get_request(request_id):
    # Получаем основную информацию о заявке
    request = await db.fetchrow(
        '''SELECT r.id, u.full_name, u.phone_number, 
           r.request_text, r.photo_id, r.request_date
           FROM requests r
           JOIN users u ON r.user_id = u.user_id
           WHERE r.id = $1''',
        request_id
    )
    return request
    
async def get_request_tags(request_id) -> list:
    """Получает все теги для конкретной заявки"""
    tags = await db.fetch(
        '''SELECT tag FROM request_tags
        WHERE request_id = $1
        ORDER BY tag''',
        request_id
    )
    return [tag['tag'] for tag in tags]