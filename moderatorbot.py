import time
from datetime import datetime
import logging
import os

from db import Database

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import *

logging.basicConfig(level=logging.INFO)

TOKEN = 'YOUR BOT TOKEN'

database = Database('database.db')
bot = Bot(token=TOKEN, parse_mode='html')
dp = Dispatcher(bot)
mute_sec = 0
moderators = ["LIST OF MODERATORS IDS"]


@dp.message_handler(commands=['mute'])
async def mute(message: types.Message):
    global mute_sec, moderators
    try:
        if str(message.from_user.id) in moderators:

            if message.reply_to_message:

                if message.reply_to_message.from_user.id == "SOME BOT ID":
                    await message.reply_to_message.reply(
                        f'<b>Невозможно замутить бота, {message.from_user.first_name}!</b>')

                elif message.reply_to_message.from_user.id != "ADMIN'S ID":

                    mute_sec = int(message.text[6:])

                    database.add_mute(message.reply_to_message.from_user.id, mute_sec)

                    await message.delete()
                    await message.reply_to_message.reply(f'<b>{message.from_user.first_name.capitalize()}'
                                                         f' замутил пользователя '
                                                         f'{message.reply_to_message.from_user.first_name.capitalize()}'
                                                         f' на '
                                                         f'{mute_sec}'
                                                         f' сек.</b>')

                    print(message.reply_to_message.from_user.id)

                else:

                    if message.from_user.id != message.reply_to_message.from_user.id:
                        await message.delete()

                        database.add_mute(message.from_user.id, 10)
                        await message.reply_to_message.reply(f'Нельзя выдать мут создателю группы, '
                                                             f'<b>{message.from_user.first_name.capitalize()}</b>.\n\n'
                                                             f'Вам выдался мут на 10 секунд за покушение'
                                                             f' на администратора.'
                                                             )

                    else:
                        await message.reply_to_message.reply('Зачем вам мутить самого себя?')

            else:
                await message.reply('<b>Эта команда должна быть ответом на сообщение!</b>')

        else:
            await message.reply('<b>Использовать эту команду могут только администратор и модераторы!</b>',
                                parse_mode='html')

    except ValueError:
        await message.delete()
        await message.reply_to_message.reply(f"Количество секунд задано неверно!\n\n"
                                             f"Попробуйте так:   <b>/mute 10</b>.")
    except IndexError:
        await message.delete()
        await message.reply_to_message.reply(f"Количество секунд задано неверно!\n\n"
                                             f"Попробуйте так:   <b>/mute 10</b>.")


@dp.message_handler(commands=['unmute'])
async def unmute(message: types.Message):
    global mute_sec, moderators

    if str(message.from_user.id) in moderators:
        if message.reply_to_message:
            mute_sec = 0

            database.add_mute(message.reply_to_message.from_user.id, mute_sec)

            await message.delete()
            await message.reply_to_message.reply(f'<b>{message.from_user.first_name.capitalize()}'
                                                 f' размутил пользователя '
                                                 f'{message.reply_to_message.from_user.first_name.capitalize()}</b>.')

        else:
            await message.reply('<b>Эта команда должна быть ответом на сообщение!</b>')

    else:
        await message.reply('<b>Использовать эту команду могут только администратор и модераторы!</b>')


@dp.message_handler()
async def filter_messages(message: types.Message):
    if not database.examination(message.from_user.id):
        database.add(message.from_user.id)

    if database.mute(message.from_user.id):
        await message.delete()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)
