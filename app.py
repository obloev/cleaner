import logging

from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.exceptions import MessageCantBeDeleted

from commands import set_default_commands
from config import ADMIN, BOT_TOKEN
from database import Chat, connect_db
from langs import langs

bot: Bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp: Dispatcher = Dispatcher(bot, storage=storage)

logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s]  %(message)s', level=logging.INFO)


async def on_startup(dispatcher):
    try:
        await connect_db()
        await set_default_commands(dispatcher)
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
    if not await Chat.chat_exist(message.chat.id):
        await Chat.create_chat(message.chat.id, members)
    lang = await Chat.get_lang(message.chat.id)
    username = message.from_user.username
    user = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if user.status in ['creator', 'administrator'] or username == 'GroupAnonymousBot':
        await message.answer(langs[lang]['hi'])
    else:
        await message.delete()


@dp.message_handler(lambda m: m.chat.type in ['group', 'supergroup'], commands=['uz'])
async def set_uz_handler(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    username = message.from_user.username
    user = await bot.get_chat_member(chat_id, user_id)
    if user.status in ['creator', 'administrator'] or username == 'GroupAnonymousBot':
        await Chat.set_uz(message.chat.id)
        members = await bot.get_chat_members_count(message.chat.id)
        await Chat.refresh_members(message.chat.id, members)
        await message.reply("Bot tili sifatida 🇺🇿 o'zbek tili o'rnatildi")
    else:
        await message.delete()


@dp.message_handler(lambda m: m.chat.type in ['group', 'supergroup'], commands=['en'])
async def set_uz_handler(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    username = message.from_user.username
    user = await bot.get_chat_member(chat_id, user_id)
    if user.status in ['creator', 'administrator'] or username == 'GroupAnonymousBot':
        await Chat.set_rn(message.chat.id)
        members = await bot.get_chat_members_count(message.chat.id)
        await Chat.refresh_members(message.chat.id, members)
        await message.reply("The language was set to 🇺🇸 english")
    else:
        await message.delete()


@dp.message_handler(content_types=['new_chat_members', 'left_chat_member'])
async def delete_messages(message: types.Message):
    lang = await Chat.get_lang(message.chat.id)
    try:
        await message.delete()
        members = await bot.get_chat_members_count(message.chat.id)
        await Chat.refresh_members(message.chat.id, members)
        if message.content_type == 'new_chat_members':
            user = message.new_chat_members[0]
            await message.answer(
                f'👋 {langs[lang]["HI"]} <a href="tg://user?id={user.id}">{user.full_name}</a>')
    except MessageCantBeDeleted:
        await message.reply(langs[lang]['make-admin'])


@dp.message_handler(lambda m: m.entities and m.chat.type in ['group', 'supergroup'])
async def delete_links(message: types.Message):
    lang = await Chat.get_lang(message.chat.id)
    user_id = message.from_user.id
    username = message.from_user.username
    chat_id = message.chat.id
    user = await bot.get_chat_member(chat_id, user_id)
    if user.status not in ['creator', 'administrator'] and username != 'GroupAnonymousBot':
        try:
            for entity in message.entities:
                if entity.type in ['url', 'text_link', 'mention', 'bot_command']:
                    await message.delete()
                    await message.answer(
                        f'🚫 <a href="tg://user?id={message.from_user.id}">{message.from_user.full_name}</a> '
                        f"{langs[lang]['ad']}")
        except MessageCantBeDeleted:
            await message.reply(langs[lang]['make-admin'])


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
