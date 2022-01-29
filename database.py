import logging
from gino import Gino

from config import POSTGRES_URI

db: Gino = Gino()


async def connect_db() -> None:
    await db.set_bind(POSTGRES_URI)
    await db.gino.create_all()
    logging.info('Connected to DB')


class Chat(db.Model):
    __tablename__: str = 'cleaner'

    id = db.Column(db.Integer(), primary_key=True)
    chat_id = db.Column(db.BigInteger())
    members = db.Column(db.Integer(), default=0)
    lang = db.Column(db.String(), default='en')

    def __str__(self):
        return f'<Chat {self.id}>'

    @staticmethod
    async def create_chat(chat_id, members, lang='en'):
        new_chat = Chat()
        new_chat.chat_id = chat_id
        new_chat.members = members
        new_chat.lang = lang
        await new_chat.create()
        return new_chat

    @staticmethod
    async def get_chat(chat_id):
        chat = await Chat.query.where(Chat.chat_id == chat_id).gino.first()
        return chat

    @staticmethod
    async def get_chats():
        chats = await Chat.query.where(True).gino.all()
        return chats

    @staticmethod
    async def chat_exist(chat_id) -> bool:
        chat = await Chat.get_chat(chat_id)
        return bool(chat)

    @staticmethod
    async def chats_count() -> tuple[int, int]:
        chats, users = await Chat.get_chats(), 0
        for chat in chats:
            users += chat.members
        return len(chats), users

    @staticmethod
    async def refresh_members(chat_id, members):
        chat = await Chat.get_chat(chat_id)
        return await chat.update(members=members).apply()

    @staticmethod
    async def set_uz(chat_id):
        try:
            chat = await Chat.get_chat(chat_id)
            return await chat.update(lang='uz').apply()
        except:
            await Chat.delete_chat(chat_id)
            await Chat.create_chat(chat_id, 0, 'uz')

    @staticmethod
    async def set_en(chat_id):
        chat = await Chat.get_chat(chat_id)
        return await chat.update(lang='en').apply()

    @staticmethod
    async def get_lang(chat_id):
        chat = await Chat.get_chat(chat_id)
        return chat.lang

    @staticmethod
    async def delete_chat(chat_id):
        await Chat.delete.where(Chat.chat_id == chat_id).gino.status()
