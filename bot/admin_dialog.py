from aiogram_dialog import Dialog, Window
from bot_instans import dp, bot_storage_key
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.kbd import Button, Row, Next
from aiogram_dialog.widgets.input import MessageInput
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
import pickle
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ContentType
import asyncio
import translators
from requests.exceptions import HTTPError
from aiogram.exceptions import TelegramForbiddenError
from postgres_functions import return_user_wanted_spam

class ADMIN(StatesGroup):
    first = State()
    accept_msg = State()
    admin_send_msg = State()

async def button_zagruz_db(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    with open('save_db.pkl', 'rb') as file:
        recover_base = pickle.load(file)
        await dp.storage.set_data(key=bot_storage_key, data=recover_base)
    await callback.message.answer('База данных успешно загружена !')
    await dialog_manager.done()  # выход из режима админа


async def button_save_db(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
    with open('save_db.pkl', 'wb') as file:
        pickle.dump(bot_dict, file)
    await callback.message.answer('База данных успешно записана !')
    await dialog_manager.done()  # выход из режима админа

async def accepet_admin_message(msg:Message, widget: MessageInput, dialog_manager: DialogManager, *args, **kwargs):
    dialog_manager.dialog_data['admin_msg'] = msg.text
    await dialog_manager.next()

async def message_sender(slovo:str, lan:str, temp_dict:dict)->str:
    if lan != 'en':
        try:
            if lan not in temp_dict:
                res = translators.translate_text(query_text=slovo, from_language='en', to_language=lan, translator='alibaba')
                temp_dict[lan]=res
            else:  # Если перевод уже есть - то отправляй перевод и не переводи снова
                res = temp_dict[lan]
        except AttributeError:
                print('\n\n произошла ошибка AttributeError')
                res = 'Es ist ein Fehler aufgetreten, versuchen Sie bitte noch mal'
        except HTTPError:
            print('Произошла ошибка HTTPError:\n\n')
            res = slovo
        except Exception as err:
            print(f'Other error occurred: {err}')
            res = slovo
    else:
        res = slovo
    return res

async def sending_msg(cb:CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
        temp_dict = {}
        text_from_admin = dialog_manager.dialog_data['admin_msg']
        spam_list = await return_user_wanted_spam()  # Делаю запрос к постгресу [(66234524532, 'ru'), (63234524532, 'ru')]
        for us_tuple in spam_list:  # us_tuple =  (66234524532, 'ru')
            lan = us_tuple[1]
            # print('lan = ', lan)
            chat_id = us_tuple[0]
            if not text_from_admin.startswith('🔸'):  # Сообщение без ссылки на бота
                spam = await message_sender(text_from_admin[1:], lan, temp_dict) # Отсоединяю 🔸
            else:
                temp_text, bot_teil = text_from_admin.split('@') # Сообщение со ссылкой на бот
                halb_spam = await message_sender(temp_text, lan, temp_dict)
                spam = halb_spam +'\n\n@'+bot_teil
            try:
                decorated_spam ='🔸 '+spam
                await cb.bot.send_message(chat_id=chat_id, text=decorated_spam)
            except TelegramForbiddenError:
                pass
            except Exception as ex:
                print(f'Admin sending exception happend  {ex}')
            await asyncio.sleep(0.2)  # Жду 0.2 секунды
        temp_dict.clear()
        await cb.message.answer('Mailing done')
        await dialog_manager.done()


admin_dialog = Dialog(
    Window(
        Const('Возможные дейсвтия'),
        Next(
                    text=Const('Отправить сообщение юзерам'),
                    id='send_msg'),
        Row(
            Button(
                text=Const('Загрузить БД'),
                id='zagruz_bd',
                on_click=button_zagruz_db),
            Button(
                text=Const('Сохранить БД'),
                id='save_bd',
                on_click=button_save_db),
            ),

        state=ADMIN.first,
    ),
    Window(  #
        Const(text='введите текст сообщения'),
        MessageInput(
            func=accepet_admin_message,
            content_types=ContentType.TEXT,
        ),
        state=ADMIN.accept_msg
    ),
    Window(
        Const('Отправить сообщуху'),
        Button(
                text=Const('Отправить сообщение юзерам'),
                id='send_msg',
                on_click=sending_msg),
        state=ADMIN.admin_send_msg)

)













