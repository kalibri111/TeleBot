from settings import bot
from geolocation import get_location
from postgres_stuff import get_state, STATE, update_state, execute

from enum import Enum

import psycopg2


@bot.message_handler(
    commands=['add'],
    func=lambda msg: get_state(msg) == STATE.START.value[0] or
                     get_state(msg) is None
)
def add_start_handler(message):
    bot.send_message(message.chat.id, 'Добавьте новое место')
    update_state(message)
    execute(
        'insert into place(chat_id, address, location) values ({}, null, null);'.
            format(message.chat.id)
    )


@bot.message_handler(func=lambda msg: get_state(msg) == STATE.PLACE.value[0])
def add_place_handler(message):
    execute(
        'update place set address = \'{}\' where chat_id = {};'.format(
            message.text, message.chat.id
        )
    )
    bot.send_message(message.chat.id, 'Добавьте адрес')
    update_state(message)


@bot.message_handler(func=lambda msg: get_state(msg) == STATE.LOCATION.value[0])
def add_location_handler(message):
    execute(
        'update place set location = \'{}\' where chat_id = {}'.format(
            message.text, message.chat.id
        )
    )
    update_state(message)
    bot.send_message(message.chat.id, 'Подтвердите сохранение')


@bot.message_handler(func=lambda msg: get_state(msg) == STATE.CONFIRMATION.value[0])
def add_confirmation_handler(message):
    if 'нет' in message.text:
        execute(
            'delete from place where chat_id = {}'.format(message.chat.id)
        )
        bot.send_message(message.chat.id, 'Отменено')
    else:
        bot.send_message(message.chat.id, 'Успешно сохранено')
    update_state(message)
