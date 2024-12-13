from bot_instans import bot, scheduler
import time
from datetime import datetime
from bot_instans import baza_id


async def mahnung_gearbeitet(user_id, mahnung_data, time_stamp):
    print('WE are into mahnung gearbeitet function')
    formatted_date = f'‼️ <b>MAHNUNG   {time_stamp}</b>'
    if mahnung_data.startswith('🔶'):
        titel = formatted_date +'\n\n' + mahnung_data
        await bot.send_message(chat_id=user_id, text=titel)
    else:
        await bot.send_photo(chat_id=user_id, photo=mahnung_data, caption=formatted_date)


def scheduler_job(user_id, dialog_dict, tz:str):
    int_za_chas = int(dialog_dict['za_chas'])
    future = datetime.fromtimestamp(int_za_chas)  # Время когда действие должно быть закончено
    print('future = ', future, type(future))
    id = str(user_id) + str(dialog_dict['za_chas'])
    print('tz = ', tz)
    baza_id.append(str(dialog_dict['za_chas']))
    if dialog_dict['titel']:
        mahnung_data ='🔶  ' + dialog_dict['titel']
    else:
        mahnung_data = dialog_dict['foto_id']
    time_stamp = dialog_dict['real_time']  # 28.11.2024  13:50 <class 'str'>
    # print('37 time stamp = ', time_stamp, type(time_stamp))
    scheduler.add_job(mahnung_gearbeitet, "date", run_date=future, timezone=tz, args=(user_id, mahnung_data, time_stamp), id=id)
    time.sleep(0.2)


async def mahnung_za_sutki_gearbeitet(user_id, mahnung_data, time_stamp):
    print('WE are into mahnung gearbeitet za sutki function')
    formatted_date = f'‼️ <b>MAHNUNG   {time_stamp}</b>'
    if mahnung_data.startswith('🔶'):
        titel = formatted_date + '\n\n' + mahnung_data
        await bot.send_message(chat_id=user_id, text=titel)
    else:
        await bot.send_photo(chat_id=user_id, photo=mahnung_data, caption=formatted_date)

def scheduler_za_sutki_job(user_id:int, dialog_dict, tz:str):
    future_za_sutki = datetime.fromtimestamp(dialog_dict['za_sutki'])  # Время когда действие должно быть закончено
    # tz = dialog_dict['tz']
    id = str(user_id)+str(dialog_dict['za_sutki'])
    if dialog_dict['titel']:
        mahnung_data ='🔶  ' + dialog_dict['titel']
    else:
        mahnung_data = dialog_dict['foto_id']
    time_stamp = dialog_dict['real_time']
    scheduler.add_job(mahnung_za_sutki_gearbeitet, "date", run_date=future_za_sutki, timezone=tz, args=(user_id, mahnung_data, time_stamp), id=id)
    time.sleep(0.2)



async  def napominalka_async_for_month(user_id, mahnung_data, time_data):
    formatted_date = f'🔆 <b>MAHNUNG   {time_data}</b>'
    if mahnung_data.startswith('🔶'):
        titel = formatted_date + '\n\n' + mahnung_data
        await bot.send_message(chat_id=user_id, text=titel)
    else:
        await bot.send_photo(chat_id=user_id, photo=mahnung_data, caption=formatted_date)


def napominalka_sync_for_month(user_id, dialog_dict:dict):
    print('napominalka_sync works')
    temp_days = set(dialog_dict['day'].split(','))
    t = ''
    for x in temp_days:
        t+=x+','
    day_of_month = t[:-1]
    chas = int(dialog_dict['hours'])  # интую
    minutusy = int(dialog_dict['minuts'])
    if dialog_dict['titel']:
        mahnung_data ='🔶  ' + dialog_dict['titel']
    else:
        mahnung_data = dialog_dict['foto_id']
    data_s_tochkami = dialog_dict['real_time']
    # time_data =  data_s_tochkami.replace(',', '').replace(':', '').replace(' ','')
    # print('time_data = ', time_data)
    tz = dialog_dict['tz']
    job_id =dialog_dict['job_id']

    id = str(user_id) + job_id  # 6685637602301550
    # print('id = ', id)
    scheduler.add_job(napominalka_async_for_month, "cron", day=day_of_month, hour = chas,
                      minute = minutusy, end_date='2037-05-30',  timezone=tz,
                      args=(user_id, mahnung_data, data_s_tochkami), id=id)
#####################################################################################

async  def async_week_sched(user_id, mahnung_data, time_data):
    formatted_date = f'⭐️ <b>MAHNUNG   {time_data}</b>'
    if mahnung_data.startswith('🔹'):
        titel = formatted_date + '\n\n' + mahnung_data
        await bot.send_message(chat_id=user_id, text=titel)
    else:
        await bot.send_photo(chat_id=user_id, photo=mahnung_data, caption=formatted_date)


def week_sched(user_id, dialog_dict:dict):
    print('week_sched_sync works')
    week_days = dialog_dict['week_days']
    # print('week_days = ', week_days)
    # dni_nedeli = week_day_bearbeiten(week_days.split(','))
    # print('dni_nedeli = ', dni_nedeli)
    chas = int(dialog_dict['hours'])  # интую
    minutusy = int(dialog_dict['minuts'])
    if dialog_dict['titel']:
        mahnung_data ='🔹  ' + dialog_dict['titel']
    else:
        mahnung_data = dialog_dict['foto_id']
    week_key = dialog_dict['key']
    # print('week_key = ', week_key)
    r_t = dialog_dict['real_time']
    # print('r_t= ', r_t)
    id = str(user_id) + week_key  # 6685637602301550
    print('week = ', dialog_dict)
    tz = dialog_dict['tz']
    scheduler.add_job(async_week_sched, "cron", day_of_week=week_days, hour = chas,
                      minute = minutusy, end_date='2037-05-30',  timezone=tz,
                      args=(user_id, mahnung_data, r_t), id=id)

########################################################################################

async  def async_day_sched(user_id, mahnung_data, time_data):
    formatted_date = f'🔔 <b>MAHNUNG   {time_data}</b>'
    if mahnung_data.startswith('♦️'):
        titel = formatted_date + '\n\n' + mahnung_data
        await bot.send_message(chat_id=user_id, text=titel)
    else:
        await bot.send_photo(chat_id=user_id, photo=mahnung_data, caption=formatted_date)


def day_sched(user_id, dialog_dict:dict):
    print('day_sched_sync works')
    chas = dialog_dict['hours']
    # print('chas in shed = ', chas)
    minutusy = dialog_dict['minuts']
    if dialog_dict['titel']:
        mahnung_data ='♦️  ' + dialog_dict['titel']
    else:
        mahnung_data = dialog_dict['foto_id']
    day_key = dialog_dict['key']
    print('day_key = ', day_key)
    r_t = dialog_dict['real_time']
    # print('r_t= ', r_t)
    id = str(user_id) + day_key  # 6685637602011550
    # print('day_dict = ' , dialog_dict)
    tz = dialog_dict['tz']
    scheduler.add_job(async_day_sched, "cron", hour = chas,
                      minute = minutusy, end_date='2037-05-30',  timezone=tz,
                      args=(user_id, mahnung_data, r_t), id=id)