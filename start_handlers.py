from settings import bot


@bot.message_handler(commands=['start'])
def start_handler(message):
    help_str = '/add - добавление места, если ввели неправильно, в конце введите \'нет\'' \
               '/list - вывод последних 10 мест' \
               '/reset - удалить все ваши места'
    bot.send_message(message.chat.id, help_str)
