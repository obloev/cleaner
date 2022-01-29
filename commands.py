from aiogram import types, Dispatcher


async def set_default_commands(dp: Dispatcher) -> None:
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "🤖 Launch the bot"),
            types.BotCommand("uz", "Bot tilini 🇺🇿 o'zbekcha qilish"),
            types.BotCommand("en", "Set the bot language to 🇺🇸 english"),
        ], scope=types.BotCommandScopeAllGroupChats()
    )
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "🤖 Launch the bot"),
        ]
    )
