# За основу взята разработка автора Kojihov с форума https://zelenka.guru/

import os
import json
import openai
import telebot
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("AI_TOKEN")
bot = telebot.TeleBot(os.getenv("TG_TOKEN"))

if not os.path.exists("users"):
    os.mkdir("users")


@bot.message_handler(content_types=['text'])
def msg(message):
    if f"{message.chat.id}.json" not in os.listdir('users'):
        with open(f"users/{message.chat.id}.json", "x") as open_file_wr:
            open_file_wr.write('')

    with open(f'users/{message.chat.id}.json', 'r') as open_file_r:
        old_messages = open_file_r.read()

    if message.text == '/clear':
        with open(f'users/{message.chat.id}.json', 'w') as open_file_wr_clear:
            open_file_wr_clear.write('')
        return bot.send_message(chat_id=message.chat.id, text='История очищена!')

    try:
        send_message = bot.send_message(chat_id=message.chat.id, text='Обрабатываю запрос, пожалуйста подождите!')
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=[{"role": "user", "content": old_messages},
                      {"role": "user", "content": f'Предыдущие сообщения: {old_messages}; Запрос: {message.text}'}],
            presence_penalty=0.6)

        bot.edit_message_text(text=completion.choices[0].message["content"], chat_id=message.chat.id,
                              message_id=send_message.message_id)

        from_json = {'id': completion.id + '\n', 'request': message.text + '\n', 'answer': completion.choices[0].message["content"] + '\n'}

        with open(f'users/{message.chat.id}.json', 'a', encoding='utf-8') as open_file_wr_message:
            json.dump(from_json, open_file_wr_message)



        # with open(f'users/{message.chat.id}.json', 'r', encoding='utf-8') as open_file_r_message:
        #     lines = open_file_r_message.readlines()
        #
        # if len(lines) >= int(os.getenv("NUMBER_MESSAGE")):
        #     with open(f'users/{message.chat.id}.json', 'w', encoding='utf-8') as open_file_wr_len:
        #         open_file_wr_len.writelines(lines[2:])

    except Exception as e:
        if str(e) == '<empty message>':
            bot.send_message(chat_id=message.chat.id, text=f'Отправлено пустое сообщение!')
        else:
            bot.send_message(chat_id=message.chat.id, text=str(e))


bot.infinity_polling()
