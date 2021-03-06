from aiogram import types, Dispatcher


async def set_default_commands(dp: Dispatcher) -> None:
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "π€ Launch the bot"),
            types.BotCommand("uz", "Bot tilini πΊπΏ o'zbekcha qilish"),
            types.BotCommand("en", "Set the bot language to πΊπΈ english"),
        ], scope=types.BotCommandScopeAllGroupChats()
    )
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "π€ Launch the bot"),
        ]
    )
