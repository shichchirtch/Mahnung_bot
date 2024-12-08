from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, ManagedRadio
from aiogram_dialog.api.entities.modes import ShowMode
from postgres_functions import insert_lan, insert_lan_in_spam, return_lan, return_tz


async def set_lan(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    dialog_manager.dialog_data['lan']= callback.data
    lan = callback.data
    us_lan_in_postgress = await return_lan(callback.from_user.id)
    if us_lan_in_postgress != lan:
        await insert_lan(callback.from_user.id, lan)  # Вставляю язык в постгрес
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await dialog_manager.next()

async def radio_spam_button_clicked(callback: CallbackQuery, radio: ManagedRadio, dialog_manager: DialogManager, *args, **kwargs):
    user_id = callback.from_user.id
    temp_dict = {'1': {'ru':'Ну и ладно', 'en':'no problem', 'de':'kein Problem', 'tr':'sorun değil', 'uk': 'немає проблем',
                       'fa': 'مشکلی نیست',
                       'ar':'لا مشكلة'},
                 '2': {'ru':'Очень хорошо  😉', 'en':'Perfect !  😉', 'ar':'ممتاز ! 😉',
                       'tr':'Mükemmel !  😉', 'fa': 'عالی! 😉',
                       'uk':'Ідеально! 😉',}}
    lan = await return_lan(callback.from_user.id)
    ans_data = temp_dict[callback.data[-1]]
    print('ans_data  = ', ans_data )
    await callback.message.answer(f"{ans_data[lan]}")
    if callback.data[-1] == '2':
        await insert_lan_in_spam(user_id, lan)  # Вставляю язык в поле спам для желающих
    dialog_manager.show_mode = ShowMode.SEND
    await dialog_manager.next()


async def go_to_unique(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    dialog_manager.show_mode = ShowMode.SEND
    lan = await return_lan(callback.from_user.id)
    dialog_manager.dialog_data['lan'] = lan  # Записываю язык в короткоживующию БД, чтобы не вытаскивать его из Редиса
    print('/////manager.dialog_data = ', dialog_manager.dialog_data)
    await dialog_manager.next()


async def go_to_mahnung_dialog(callback: CallbackQuery, widget: Button, manager: DialogManager, *args, **kwargs):
    print('go_to_mahnung_dialog works')
    manager.show_mode = ShowMode.SEND


async def reset_funk(callback: CallbackQuery, widget:Button,
                     dialog_manager: DialogManager, *args, **kwargs):
    print('reset funk works')
    dialog_manager.dialog_data.clear()
    # await dialog_manager.done()#, mode=StartMode.RESET_STACK)






