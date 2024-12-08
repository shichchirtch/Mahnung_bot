from aiogram.types import BotCommand


async def set_main_menu(bot):
    main_menu_commands = [
        BotCommand(command='/basic_menu',
                   description='Go to START'),

        BotCommand(command='/help',
                   description='How to work with a bot ')

    ]
    await bot.set_my_commands(main_menu_commands)