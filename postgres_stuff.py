from enum import Enum
from settings import DATABASE_URL

import psycopg2


class STATE(Enum):
    START = 1,
    PLACE = 2,
    LOCATION = 3,
    CONFIRMATION = 4,


def execute(sql):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    r = None
    with conn:
        with conn.cursor() as curs:
            curs.execute(sql)
            if curs.rowcount and 'select' in sql.lower():
                if curs.rowcount == 1:
                    r = curs.fetchone()
                else:
                    r = curs.fetchall()
    return r


def get_state(message):
    chat_id = message.chat.id
    request = execute('select state from chat where uuid = {};'.format(chat_id))
    if request is not None:
        request = request[0]
    return request


def update_state(message):
    cur_state = get_state(message)
    new_state = None
    if cur_state is None:
        execute(
            'insert into chat(uuid, state) values ({}, {});'.format(message.chat.id, 1)
        )
        new_state = 2
    elif cur_state < 4:
        new_state = cur_state + 1
    else:
        new_state = 1
    execute(
        'update chat set state = {} where uuid = {};'.format(
            new_state, message.chat.id
        )
    )
