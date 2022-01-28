import logging

from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.exceptions import MessageCantBeDeleted

from config import ADMIN, BOT_TOKEN
from database import Chat, connect_db

bot: Bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp: Dispatcher = Dispatcher(bot, storage=storage)

logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s]  %(message)s', level=logging.INFO)


async def on_startup(dispatcher):
    try:
        await connect_db()
        await dispatcher.bot.send_message(ADMIN, "<b>🤖 Bot launched</b>")
    except Exception as err:
        logging.exception(err)


async def on_shutdown(dispatcher):
    try:
        await dispatcher.bot.send_message(ADMIN, "<b>⚠️ Bot stopped</b>")
    except Exception as err:
        logging.exception(err)


@dp.message_handler(lambda m: m.from_user.id == ADMIN, commands=['count'])
async def count(message: types.Message):
    chats, users = await Chat.chats_count()
    await message.answer(f'<b>Chats: {chats}\nUsers: {users}</b>')


@dp.message_handler(lambda m: m.chat.type == 'private', commands=['start'])
async def start(message: types.Message):
    markup = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton('Add to a group', url='https://t.me/Cleaner_OKBot?startgroup=botstart'))
    await message.answer('👋 Hi. This bot deletes ads and messages about new and left members in groups. '
                         'Add it to a group to use the bot', reply_markup=markup)


@dp.message_handler(lambda m: m.chat.type in ['group', 'supergroup'], commands=['start'])
async def start_group(message: types.Message):
    members = await bot.get_chat_members_count(message.chat.id)
    await Chat.create_chat(message.chat.id, members)
    await message.answer('👋 Hi. I delete ads and messages about new and left members in the group. '
                         'To do this, make me the group <b>admin</b>')


@dp.message_handler(content_types=['new_chat_members', 'left_chat_member'])
async def delete_messages(message: types.Message):
    try:
        await message.delete()
        members = await bot.get_chat_members_count(message.chat.id)
        await Chat.refresh_members(message.chat.id, members)
        if message.content_type == 'new_chat_members':
            await message.answer(
                f'👋 Hi <a href="tg://user?id={message.from_user.id}">{message.from_user.full_name}</a>')
    except MessageCantBeDeleted:
        await message.reply('Make me the group <b>admin</b> to delete this message')


@dp.message_handler(lambda m: m.entities and m.chat.type in ['group', 'supergroup'])
async def delete_links(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    chat_id = message.chat.id
    user = await bot.get_chat_member(chat_id, user_id)
    if user.status not in ['creator', 'administrator'] and username != 'GroupAnonymousBot':
        try:
            for entity in message.entities:
                if entity.type in ['url', 'text_link']:
                    await message.delete()
                    await message.answer(
                        f'🚫 <a href="tg://user?id={message.from_user.id}">{message.from_user.full_name}</a> '
                        f"don't distribute advertisements")
        except MessageCantBeDeleted:
            await message.reply('Make me the group <b>admin</b> to delete this ad')


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
