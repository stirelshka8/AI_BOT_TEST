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
        data_new = {'message': []}
        with open(f"users/{message.chat.id}.json", "x") as open_file_wr:
            json.dump(data_new, open_file_wr, ensure_ascii=False, indent=2)

    try:
        with open(f'users/{message.chat.id}.json', 'r', encoding='utf-8') as open_file_r:
            old_messages = json.load(open_file_r)
            old_list = []
            for old_ in old_messages['message']:
                old_list.append(old_['answer'])

            if len(old_list) > 0:
                oldus_mess = str(old_list[-1])
            else:
                oldus_mess = "Нет сообщений"
    except:
        oldus_mess = "Нет сообщений"

    if message.text == '/clear':
        data_clear = {'message': []}
        with open(f'users/{message.chat.id}.json', 'w') as open_file_wr_clear:
            json.dump(data_clear, open_file_wr_clear, ensure_ascii=False, indent=2)
        return bot.send_message(chat_id=message.chat.id, text='История очищена!')

    try:
        send_message = bot.send_message(chat_id=message.chat.id, text='Обрабатываю запрос, пожалуйста подождите!')
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=[{"role": "user", "content": oldus_mess},
                      {"role": "user", "content": f'Предыдущие сообщения: {oldus_mess}; Запрос: {message.text}'}],
            presence_penalty=0.6)

        bot.edit_message_text(text=completion.choices[0].message["content"], chat_id=message.chat.id,
                              message_id=send_message.message_id)

        from_json = {'id': completion.id, 'request': message.text, 'answer': completion.choices[0].message["content"]}

        with open(f'users/{message.chat.id}.json', encoding='utf8') as f:
            data = json.load(f)
        data['message'].append(from_json)
        with open(f'users/{message.chat.id}.json', 'w', encoding='utf8') as outfile:
            json.dump(data, outfile, ensure_ascii=False, indent=2)

    except Exception as e:
        if str(e) == '<empty message>':
            bot.send_message(chat_id=message.chat.id, text=f'Отправлено пустое сообщение!')
        else:
            print(e)


bot.infinity_polling()
