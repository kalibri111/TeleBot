from settings import bot
from postgres_stuff import execute


@bot.message_handler(commands=['reset'])
def reset_handler(message):
    execute(
        'delete from place where chat_id = {};'.format(message.chat.id)
    )
    bot.send_message(message.chat.id, 'Ваши записи успешно удалены')
