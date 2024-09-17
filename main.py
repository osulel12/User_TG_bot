from telebot.async_telebot import AsyncTeleBot
from telebot import types
from telebot.asyncio_helper import ApiTelegramException
import dotenv
import os
import asyncio
import aiofiles
from pathlib import Path
from class_bd_work import Hepl_work_by_postgre
from create_keyboard import create_replay_markup, create_inline_markup
import help_variable
from file_search import File_search
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

if os.path.exists('.env'):
    dotenv.load_dotenv('.env')


path_country_analist = r'/your/path/country/'
path_group_country_analist = r'/your/path/group_country/'


path_barier_country = r'/your/path/barier_country/'
path_region = r'/your/path/region/'

bot = AsyncTeleBot(os.getenv('TOKEN'), colorful_logs=True)

need_example_class = Hepl_work_by_postgre()


@bot.message_handler(commands=['start'])
async def start_command(message: types.Message):
    """
    Функция отвечающая за ввод команды start

    :param message: сообщение от пользователя
    """
    hello_text = await need_example_class.write_hello_func()
    chat_id = message.chat.id

    logging.info(f"user = {chat_id}, commands = start")

    # Проверка авторизации пользователя
    if await need_example_class.check_user(chat_id):
        await need_example_class.update_state_user(chat_id, 'main')
        await bot.send_message(chat_id, f'{hello_text}, выберите интересующий вас функционал 👇',
                               reply_markup=create_replay_markup('', 'main'))

    # Если пользователь зарегистрирован, но не авторизован
    elif await need_example_class.check_user(chat_id, flag_approv='not_token'):
        await bot.send_message(chat_id, f'{hello_text}, авторизируйтесь введя ваш уникальный токен')

    elif await need_example_class.check_user(chat_id, flag_approv='not_active'):
        logging.info(f'Пользователь user = {chat_id} пытался воспользоваться функционалом')

    # Если пользователь не зарегистрирован
    else:
        await bot.send_message(chat_id, f'{hello_text}, пройдите регистрацию, для этого введите команду /reg')


@bot.message_handler(commands=['reg'])
async def registration_command(message: types.Message):
    """
    Функция отвечающая за ввод команды reg

    :param message: сообщение от пользователя
    """
    chat_id = message.chat.id

    logging.info(f"user = {chat_id}, commands = reg")

    # Если пользователь уже авторизован
    if await need_example_class.check_user(chat_id):
        await need_example_class.update_state_user(chat_id, 'main')
        await bot.send_message(chat_id, 'Вы уже авторизированы', reply_markup=create_replay_markup('', 'main'))

    # Если пользователь зарегистрирован, но не авторизован
    elif await need_example_class.check_user(chat_id, flag_approv='not_token'):
        await need_example_class.update_state_user(chat_id, 'registration')
        await bot.send_message(chat_id,
                               'Вы уже зарегистрированы, пройдите авторизацию, для этого отправьте ваш уникальный токен')

    elif await need_example_class.check_user(chat_id, flag_approv='not_active'):
        logging.info(f'Пользователь user = {chat_id} пытался воспользоваться функционалом')

    # Если пользователь не зарегистрирован
    else:
        await need_example_class.add_user_in_db(chat_id)
        await need_example_class.update_state_user(chat_id, 'registration')
        await bot.send_message(chat_id,
                               """Вы успешно зарегистрированы, для авторизации отправьте ваш уникальный токен"""
                               , parse_mode='html')


@bot.message_handler(func=lambda message: need_example_class.dct_user_state[message.chat.id] == 'registration')
async def autorization_user(message: types.Message):
    """
    Функция срабатывающая, когда пользователь находится в состоянии registration

    :param message: сообщение пользователя
    """
    chat_id = message.chat.id

    if await need_example_class.validate_token(message.text,
                                               os.getenv('ID_SERVICE')) and await need_example_class.check_user(chat_id,
                                                                                                                flag_approv='not_token'):
        await need_example_class.update_token_user(chat_id, message.text)
        await need_example_class.update_state_user(chat_id, 'main')
        await bot.delete_message(chat_id, message.message_id)
        await bot.send_message(chat_id, 'ℹ️ Вы успешно авторизированы!', reply_markup=create_replay_markup('', 'main'))
    else:
        await bot.send_message(chat_id, 'Некорректный токен')


@bot.message_handler(func=lambda message: need_example_class.dct_user_state[message.chat.id] == 'main')
async def main_bot_menue(message: types.Message):
    """
    Функция срабатывающая, когда пользователь находится в состоянии main

    :param message: сообщение пользователя
    """
    chat_id = message.chat.id
    message_text = message.text

    logging.info(f"user = {chat_id}, state = {need_example_class.dct_user_state[chat_id]}, message = {message_text}")

    if await need_example_class.get_access_section(chat_id,
                                                   message_text[2:]) and message_text == '📤 Аналитика внешних рынков':
        await need_example_class.update_state_user(chat_id, 'analist')
        await bot.send_message(chat_id, 'Выберите раздел 👇', reply_markup=create_replay_markup(message_text, 'analist'))

    elif await need_example_class.get_access_section(chat_id, message_text[
                                                              2:]) and message_text == '🚧 Тарифные/Нетарифные барьеры':
        await need_example_class.update_state_user(chat_id, 'barier')
        await bot.send_message(chat_id, 'Выберите раздел 👇', reply_markup=create_replay_markup(message_text, 'barier'))

    elif await need_example_class.get_access_section(chat_id, message_text[
                                                              2:]) and message_text == '🏞 Региональная аналитика':
        await need_example_class.update_state_user(chat_id, 'region')
        await bot.send_message(chat_id, 'Выберите раздел 👇', reply_markup=create_replay_markup(message_text, 'region'))

    elif await need_example_class.get_access_section(chat_id, message_text[
                                                              2:]) and message_text == '📩 Управление рассылкой':
        list_user_alert = await need_example_class.get_alert_description(chat_id)
        if len(list_user_alert) > 0:
            await need_example_class.update_state_user(chat_id, 'subscribe')
            pagination_status = await need_example_class.get_pagination_status(chat_id)
            await bot.send_message(chat_id, 'Выберите рассылку, статус которой хотите изменить 📨',
                                   reply_markup=create_inline_markup(state='subscribe',
                                                                     list_itemns=list_user_alert,
                                                                     pagen=pagination_status,
                                                                     element_on_page=5))
        else:
            await bot.send_message(chat_id,
                                   'Нет доступных рассылок',
                                   reply_markup=create_replay_markup('', 'main')
                                   )

    elif await need_example_class.get_access_section(chat_id, message_text[
                                                              2:]) and message_text == '🤖 Что умеет бот':
        await bot.send_message(chat_id, help_variable.instruction_text, parse_mode='html')

    else:
        await bot.send_message(chat_id, '🕵🏻‍♂️ Такой команды не существует, либо у вас нет доступа, возможно, вам поможет команада /start')


@bot.message_handler(func=lambda message: need_example_class.dct_user_state[message.chat.id] == 'analist')
async def analytical_section(message: types.Message):
    """
    Функция срабатывающая, когда пользователь находится в состоянии analist

    :param message: сообщение пользователя
    """
    chat_id = message.chat.id
    message_text = message.text

    logging.info(f"user = {chat_id}, state = {need_example_class.dct_user_state[chat_id]}, message = {message_text}")

    if await need_example_class.get_access_section(chat_id, message_text[2:]) and message_text == '📜 Страновые справки':
        await bot.send_message(chat_id, 'Для выбора страны/группы стран воспользуетесь кнопками 💡',
                               reply_markup=create_replay_markup(message_text, 'analist'))

    elif await need_example_class.get_access_section(chat_id, message_text[2:]) and message_text == '📔 Перечень стран':
        await need_example_class.update_state_user(chat_id, 'analist_country')
        # Фильтруем страны, для пользователей с ролью не admin
        list_country = await need_example_class.filter_country_nnn(chat_id, os.listdir(path_country_analist))
        pagination_status = await need_example_class.get_pagination_status(chat_id)
        await bot.send_message(chat_id, 'Доступные страны:', parse_mode='markdown',
                               reply_markup=create_inline_markup('analist_country', list_country, pagination_status))

    elif await need_example_class.get_access_section(chat_id, message_text[2:]) and message_text == '📕 Перечень групп':
        await need_example_class.update_state_user(chat_id, 'analist_group_country')
        # Фильтруем страны, для пользователей с ролью не admin
        list_country = await need_example_class.filter_country_nnn(chat_id, os.listdir(path_group_country_analist))
        pagination_status = await need_example_class.get_pagination_status(chat_id)
        await bot.send_message(chat_id, 'Доступные страны:', parse_mode='markdown',
                               reply_markup=create_inline_markup('analist_group_country', list_country,
                                                                 pagination_status, element_on_page=9))

    elif await need_example_class.get_access_section(chat_id, message_text[2:]) and message_text == '🚪 В главное меню':
        await need_example_class.update_state_user(chat_id, 'main')
        await bot.send_message(chat_id, 'Вы вернулись в главное меню!', reply_markup=create_replay_markup('', 'main'))

    elif await need_example_class.get_access_section(chat_id, message_text[2:]) and message_text == '🔙 Назад':
        await bot.send_message(chat_id, 'Выберите раздел 👇', reply_markup=create_replay_markup(message_text, 'analist'))

    else:
        await bot.send_message(chat_id, '🕵🏻‍♂️ Такой команды не существует, либо у вас нет доступа, возможно, вам поможет команада /start')


@bot.callback_query_handler(
    func=lambda call: need_example_class.dct_user_state[call.message.chat.id] == 'analist_country')
async def call_back_analytical_country(call: types.CallbackQuery):
    """
    Функция срабатывающая, когда пользователь находится в состоянии analist_country

    :param call: call_back с inline keyboard
    """
    call_text = call.data
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    logging.info(f"user = {chat_id}, state = {need_example_class.dct_user_state[chat_id]}, callback = {call_text}")

    # Фильтруем страны, для пользователей с ролью не admin
    list_country = await need_example_class.filter_country_nnn(chat_id, os.listdir(path_country_analist))

    # Управление пагинацией для становых справок
    if call_text in ['next', 'back'] and await need_example_class.check_user(chat_id):
        pagination_status = await need_example_class.get_pagination_status(chat_id, call_text)
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="Доступные страны:",
            parse_mode="markdown",
            reply_markup=create_inline_markup('analist_country', list_country, pagination_status))

    # Отправляем справки по форме 1,2 пользователю
    elif call_text in list_country and await need_example_class.check_user(chat_id):
        list_not_none_form = []
        path_full = path_country_analist + call_text
        way_pah_values = Path(path_full)
        need_search = File_search(way_pah_values)
        forma1 = need_search.get_actual_form1()
        forma2 = need_search.get_actual_form2()
        await bot.delete_message(chat_id, message_id)
        if forma2 != '':
            list_not_none_form.append('f2')
            async with aiofiles.open(forma2, 'rb') as f2:
                await bot.send_document(chat_id, f2, caption='Справка по форме 2')
        else:
            await bot.send_message(chat_id, 'Форма 2 отсутствует')
        if '' in forma1:
            await bot.send_message(chat_id, 'Форма 1 отсутствует')
        else:
            list_not_none_form.append('f1')
            async with aiofiles.open(forma1[0], 'rb') as f1, aiofiles.open(forma1[1], 'rb') as fx:
                await bot.send_media_group(chat_id, [types.InputMediaDocument(f1),
                                                     types.InputMediaDocument(fx, caption='Справки по форме 1')])

        # Отправляем сообщение о возможности выбора версии справок, если такие есть
        if list_not_none_form:
            await bot.send_message(chat_id, f'Выбрать справки на определенную дату 📅',
                                   reply_markup=create_inline_markup('form_version_country', list_not_none_form,
                                                                     country_state=call_text))

        await need_example_class.update_state_user(chat_id, 'analist')
        await need_example_class.insert_logging_in_db(chat_id, call_text, datetime.now(),
                                                      'Актуальные страновые справки')


@bot.callback_query_handler(
    func=lambda call: call.data.split('.')[0] in ['form2_version_country', 'form1_version_country'])
async def get_keyboard_version_form(call: types.CallbackQuery):
    """
    Функция срабатывающая, когда получает определенный callback из списка
    Нужна для отправки вариантов даты выбранной справки

    :param call: call_back с inline keyboard
    """

    chat_id = call.message.chat.id

    logging.info(f"user = {chat_id}, state = {need_example_class.dct_user_state[chat_id]}")

    if await need_example_class.check_user(chat_id):
        current_state = await need_example_class.get_current_state(chat_id)
        if current_state in ['form2_version_country', 'form1_version_country', 'form2_version_group',
                             'form1_version_group']:
            await bot.send_message(chat_id=chat_id,
                                   text=f'Сначала завершите выбор даты для формы{1 if "1" in current_state else 2}')
        else:
            call_text = call.data.split('.')[0]
            call_text_country = call.data.split('.')[1]
            message_id = call.message.message_id
            await need_example_class.update_section_bot(chat_id, call_text_country)
            pagination_status = await need_example_class.get_pagination_status(chat_id)
            path_full = path_country_analist + call_text_country
            way_pah_values = Path(path_full)
            file_search = File_search(way_pah_values)
            # В зависимости от типа справки возвращаем нужную клавиатуру
            if call_text == 'form2_version_country':
                try:
                    await bot.delete_message(chat_id, message_id)
                except ApiTelegramException:
                    logging.info(f'Запрос справки по форме 2 пользователем user = {chat_id}')
                list_file_path_form2 = file_search.get_date_create_form2()
                await need_example_class.update_state_user(chat_id, 'form2_version_country')
                await bot.send_message(chat_id=chat_id, text='Выберите дату справки:',
                                       reply_markup=create_inline_markup('form2_version_country',
                                                                         list_file_path_form2, pagination_status,
                                                                         element_on_page=10))
            elif call_text == 'form1_version_country':
                try:
                    await bot.delete_message(chat_id, message_id)
                except ApiTelegramException:
                    logging.info(f'Запрос справки по форме 1 пользователем user = {chat_id}')
                list_file_path_form1 = file_search.get_date_create_form1()
                await need_example_class.update_state_user(chat_id, 'form1_version_country')
                await bot.send_message(chat_id=chat_id, text='Выберите дату справки:',
                                       reply_markup=create_inline_markup('form1_version_country',
                                                                         list_file_path_form1, pagination_status,
                                                                         element_on_page=10))
    else:
        await bot.send_message(chat_id=chat_id, text='👻')


@bot.callback_query_handler(
    func=lambda call: need_example_class.dct_user_state[call.message.chat.id] == 'form2_version_country')
async def get_version_form2(call: types.CallbackQuery):
    """
    Функция срабатывающая, когда пользователь находится в состоянии form2_version_country
    Отправляет выбранную версию страновой справки по форме 2

    :param call: call_back с inline keyboard
    """
    call_text = call.data
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    section_country = await need_example_class.get_section_bot(chat_id)
    path_full = path_country_analist + section_country
    way_pah_values = Path(path_full)
    file_search = File_search(way_pah_values)
    list_file_path = file_search.get_date_create_form2()

    logging.info(f"user = {chat_id}, state = {need_example_class.dct_user_state[chat_id]}, callback = {call_text}")

    # Управление пагинацией для версий страновых справок по форме 2
    if call_text in ['next', 'back'] and await need_example_class.check_user(chat_id):
        pagination_status = await need_example_class.get_pagination_status(chat_id, call_text)
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Выберите дату справки:",
                                    parse_mode="markdown",
                                    reply_markup=create_inline_markup('form2_version_country', list_file_path,
                                                                      pagination_status, element_on_page=10))

    # Отправляем выбранную пользователем справку
    elif call_text in list_file_path and await need_example_class.check_user(chat_id):
        forma2 = file_search.get_need_version_form2(call_text)
        await bot.delete_message(chat_id, message_id)
        async with aiofiles.open(forma2, 'rb') as f2:
            await bot.send_document(chat_id, f2, caption=f'Справка "{section_country}" по форме 2')
        await need_example_class.update_state_user(chat_id, await need_example_class.get_previous_state(chat_id))

        # Проверка, есть ли файлы по указанной форме
        if '' not in file_search.get_actual_form1():
            await bot.send_message(chat_id, f'Выбрать справку по "{section_country}" на определенную дату 📅',
                                   reply_markup=create_inline_markup('form_version_country', ['f1'],
                                                                     country_state=section_country))

        await need_example_class.insert_logging_in_db(chat_id, section_country, datetime.now(),
                                                      'Форма 2 по стране на дату')


@bot.callback_query_handler(
    func=lambda call: need_example_class.dct_user_state[call.message.chat.id] == 'form1_version_country')
async def get_version_form1(call: types.CallbackQuery):
    """
    Функция срабатывающая, когда пользователь находится в состоянии form1_version_country
    Отправляет выбранную версию страновой справки по форме 1

    :param call: call_back с inline keyboard
    """
    call_text = call.data
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    section_country = await need_example_class.get_section_bot(chat_id)
    path_full = path_country_analist + section_country
    way_pah_values = Path(path_full)
    file_search = File_search(way_pah_values)
    list_file_path = file_search.get_date_create_form1()

    logging.info(f"user = {chat_id}, state = {need_example_class.dct_user_state[chat_id]}, callback = {call_text}")

    # Управление пагинацией для версий страновых справок по форме 1
    if call_text in ['next', 'back'] and await need_example_class.check_user(chat_id):
        pagination_status = await need_example_class.get_pagination_status(chat_id, call_text)
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Выберите дату справки:",
                                    parse_mode="markdown",
                                    reply_markup=create_inline_markup('form1_version_country', list_file_path,
                                                                      pagination_status, element_on_page=10))

    # Отправляем выбранную пользователем справку
    elif call_text in list_file_path and await need_example_class.check_user(chat_id):
        forma1_doc, forma1_xlsx = file_search.get_need_version_form1(call_text)
        await bot.delete_message(chat_id, message_id)
        async with aiofiles.open(forma1_doc, 'rb') as f1, aiofiles.open(forma1_xlsx, 'rb') as fx:
            await bot.send_media_group(chat_id, [types.InputMediaDocument(f1),
                                                 types.InputMediaDocument(fx,
                                                                          caption=f'Справка "{section_country}" по форме 1')])
        await need_example_class.update_state_user(chat_id, await need_example_class.get_previous_state(chat_id))

        # Проверка, есть ли файлы по указанной форме
        if file_search.get_actual_form2() != '':
            await bot.send_message(chat_id, f'Выбрать справку по "{section_country}" на определенную дату 📅',
                                   reply_markup=create_inline_markup('form_version_country', ['f2'],
                                                                     country_state=section_country))

        await need_example_class.insert_logging_in_db(chat_id, section_country, datetime.now(),
                                                      'Форма 1 по стране на дату')


@bot.callback_query_handler(
    func=lambda call: need_example_class.dct_user_state[call.message.chat.id] == 'analist_group_country')
async def call_back_analytical_country_group(call: types.CallbackQuery):
    """
    Функция срабатывающая, когда пользователь находится в состоянии analist_group_country
    Отправляет справки для группы стран

    :param call: call_back с inline keyboard
    """
    call_text = call.data
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    list_country = await need_example_class.filter_country_nnn(chat_id, os.listdir(path_group_country_analist))

    logging.info(f"user = {chat_id}, state = {need_example_class.dct_user_state[chat_id]}, callback = {call_text}")

    # Управление пагинацией для справок по группам стран
    if call_text in ['next', 'back'] and await need_example_class.check_user(chat_id):
        pagination_status = await need_example_class.get_pagination_status(chat_id, call_text)
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="Доступные страны:",
            parse_mode="markdown",
            reply_markup=create_inline_markup('analist_group_country', list_country, pagination_status,
                                              element_on_page=9))

    # Отправляем справки по форме 1,2 пользователю
    elif call_text in list_country and await need_example_class.check_user(chat_id):
        list_not_none_form = []
        path_full = path_group_country_analist + call_text
        way_pah_values = Path(path_full)
        need_search = File_search(way_pah_values)
        forma1 = need_search.get_actual_form1()
        forma2 = need_search.get_actual_form2()
        await bot.delete_message(chat_id, message_id)
        if forma2 != '':
            list_not_none_form.append('f2')
            async with aiofiles.open(forma2, 'rb') as f2:
                await bot.send_document(chat_id, f2, caption='Справка по форме 2',
                                        reply_markup=create_inline_markup('form2_version', [], 0))
        else:
            await bot.send_message(chat_id, 'Форма 2 отсутствует')
        if '' in forma1:
            await bot.send_message(chat_id, 'Форма 1 отсутствует')
        else:
            list_not_none_form.append('f1')
            async with aiofiles.open(forma1[0], 'rb') as f1, aiofiles.open(forma1[1], 'rb') as fx:
                await bot.send_media_group(chat_id, [types.InputMediaDocument(f1),
                                                     types.InputMediaDocument(fx, caption='Справки по форме 1')])

        if list_not_none_form:
            await bot.send_message(chat_id, f'Выбрать справки на определенную дату 📅',
                                   reply_markup=create_inline_markup('form_version_group', list_not_none_form,
                                                                     country_state=call_text))
        await need_example_class.update_state_user(chat_id, 'analist')
        await need_example_class.insert_logging_in_db(chat_id, call_text, datetime.now(),
                                                      'Актуальные справки по группам стран')


@bot.callback_query_handler(func=lambda call: call.data.split('.')[0] in ['form2_version_group', 'form1_version_group'])
async def get_keyboard_version_form_group(call: types.CallbackQuery):
    """
    Функция срабатывающая, когда call_back явялется элементом из списка
    Нужна для отправки вариантов даты выбранной справки для группы стран

    :param call: call_back с inline keyboard
    """
    chat_id = call.message.chat.id

    logging.info(f"user = {chat_id}, state = {need_example_class.dct_user_state[chat_id]}")

    if await need_example_class.check_user(chat_id):
        current_state = await need_example_class.get_current_state(chat_id)
        if current_state in ['form2_version_country', 'form1_version_country', 'form2_version_group',
                             'form1_version_group']:
            await bot.send_message(chat_id=chat_id,
                                   text=f'Сначала завершите выбор даты для формы{1 if "1" in current_state else 2}')
        else:
            call_text = call.data.split('.')[0]
            call_text_country_group = call.data.split('.')[1]
            message_id = call.message.message_id
            await need_example_class.update_section_bot(chat_id, call_text_country_group)
            pagination_status = await need_example_class.get_pagination_status(chat_id)
            path_full = path_group_country_analist + call_text_country_group
            way_pah_values = Path(path_full)
            file_search = File_search(way_pah_values)
            # В зависимости от типа справки возвращаем нужную клавиатуру
            if call_text == 'form2_version_group':
                try:
                    await bot.delete_message(chat_id, message_id)
                except ApiTelegramException:
                    logging.info(f'Запрос справки по форме 2 для групп стран пользователем user = {chat_id}')
                list_file_path_form2 = file_search.get_date_create_form2()
                await need_example_class.update_state_user(chat_id, 'form2_version_group')
                await bot.send_message(chat_id=chat_id, text='Выберите дату справки:',
                                       reply_markup=create_inline_markup('form2_version_group',
                                                                         list_file_path_form2, pagination_status,
                                                                         element_on_page=10))
            elif call_text == 'form1_version_group':
                try:
                    await bot.delete_message(chat_id, message_id)
                except ApiTelegramException:
                    logging.info(f'Запрос справки по форме 1 для групп стран пользователем user = {chat_id}')
                list_file_path_form1 = file_search.get_date_create_form1()
                await need_example_class.update_state_user(chat_id, 'form1_version_group')
                await bot.send_message(chat_id=chat_id, text='Выберите дату справки:',
                                       reply_markup=create_inline_markup('form1_version_group',
                                                                         list_file_path_form1, pagination_status,
                                                                         element_on_page=10))
    else:
        await bot.send_message(chat_id=chat_id, text='👻')


@bot.callback_query_handler(
    func=lambda call: need_example_class.dct_user_state[call.message.chat.id] == 'form2_version_group')
async def get_version_form2_group(call: types.CallbackQuery):
    """
    Функция срабатывающая, когда пользователь находится в состоянии form2_version_group
    Отправляет выбранную версию страновой справки группы стран по форме 2

    :param call: call_back с inline keyboard
    """
    call_text = call.data
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    section_country = await need_example_class.get_section_bot(chat_id)
    path_full = path_group_country_analist + section_country
    way_pah_values = Path(path_full)
    file_search = File_search(way_pah_values)
    list_file_path = file_search.get_date_create_form2()

    logging.info(f"user = {chat_id}, state = {need_example_class.dct_user_state[chat_id]}, callback = {call_text}")

    # Управление пагинацией даты для групп стран справки по форме 2
    if call_text in ['next', 'back'] and await need_example_class.check_user(chat_id):
        pagination_status = await need_example_class.get_pagination_status(chat_id, call_text)
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Выберите дату справки:",
                                    parse_mode="markdown",
                                    reply_markup=create_inline_markup('form2_version_group', list_file_path,
                                                                      pagination_status, element_on_page=10))

    # Отправляем выбранную пользователем справку
    elif call_text in list_file_path and await need_example_class.check_user(chat_id):
        forma2 = file_search.get_need_version_form2(call_text)
        await bot.delete_message(chat_id, message_id)
        async with aiofiles.open(forma2, 'rb') as f2:
            await bot.send_document(chat_id, f2, caption=f'Справка {section_country} по форме 2')
        await need_example_class.update_state_user(chat_id, await need_example_class.get_previous_state(chat_id))

        # Проверка, есть ли файлы по указанной форме
        if '' not in file_search.get_actual_form1():
            await bot.send_message(chat_id, f'Выбрать справку по "{section_country}" на определенную дату 📅',
                                   reply_markup=create_inline_markup('form_version_group', ['f1'],
                                                                     country_state=section_country))

        await need_example_class.insert_logging_in_db(chat_id, section_country, datetime.now(),
                                                      'Форма 2 по группе стран на дату')


@bot.callback_query_handler(
    func=lambda call: need_example_class.dct_user_state[call.message.chat.id] == 'form1_version_group')
async def get_version_form1_group(call: types.CallbackQuery):
    """
    Функция срабатывающая, когда пользователь находится в состоянии form1_version_group
    Отправляет выбранную версию страновой справки группы стран по форме 1

    :param call: call_back с inline keyboard
    """
    call_text = call.data
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    section_country = await need_example_class.get_section_bot(chat_id)
    path_full = path_group_country_analist + section_country
    way_pah_values = Path(path_full)
    file_search = File_search(way_pah_values)
    list_file_path = file_search.get_date_create_form1()

    logging.info(f"user = {chat_id}, state = {need_example_class.dct_user_state[chat_id]}, callback = {call_text}")

    # Управление пагинацией даты для групп стран справки по форме 1
    if call_text in ['next', 'back'] and await need_example_class.check_user(chat_id):
        pagination_status = await need_example_class.get_pagination_status(chat_id, call_text)
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Выберите дату справки:",
                                    parse_mode="markdown",
                                    reply_markup=create_inline_markup('form1_version_group', list_file_path,
                                                                      pagination_status, element_on_page=10))

    # Отправляем выбранную пользователем справку
    elif call_text in list_file_path and await need_example_class.check_user(chat_id):
        forma1_doc, forma1_xlsx = file_search.get_need_version_form1(call_text)
        await bot.delete_message(chat_id, message_id)
        async with aiofiles.open(forma1_doc, 'rb') as f1, aiofiles.open(forma1_xlsx, 'rb') as fx:
            await bot.send_media_group(chat_id, [types.InputMediaDocument(f1),
                                                 types.InputMediaDocument(fx,
                                                                          caption=f'Справка {section_country} по форме 1')])
        await need_example_class.update_state_user(chat_id, await need_example_class.get_previous_state(chat_id))

        # Проверка, есть ли файлы по указанной форме
        if file_search.get_actual_form2() != '':
            await bot.send_message(chat_id, f'Выбрать справку по "{section_country}" на определенную дату 📅',
                                   reply_markup=create_inline_markup('form_version_group', ['f2'],
                                                                     country_state=section_country))

        await need_example_class.insert_logging_in_db(chat_id, section_country, datetime.now(),
                                                      'Форма 1 по группе стран на дату')


@bot.message_handler(func=lambda message: need_example_class.dct_user_state[message.chat.id] == 'barier')
async def barier_section(message: types.Message):
    """
    Функция отвечающая за блок отдела Тарифных/Не тарифных барьеров

    :param message: сообщение от пользователя
    :return:
    """
    chat_id = message.chat.id
    message_text = message.text

    logging.info(f"user = {chat_id}, state = {need_example_class.dct_user_state[chat_id]}, message = {message_text}")

    if await need_example_class.get_access_section(chat_id,
                                                   message_text[2:]) and message_text == '📑 Ветеринарные сертификаты':
        await bot.send_message(chat_id, 'Воспользуйтесь кнопками 👇',
                               reply_markup=create_replay_markup(message_text, 'barier'))

    elif await need_example_class.get_access_section(chat_id,
                                                     message_text[2:]) and message_text == '📭 Сертификаты без ссылок':
        file_cert_name = await need_example_class.get_veterinary_certificates(chat_id, 'not_url')

        async with aiofiles.open(file_cert_name, 'rb') as file_cert:
            await bot.send_document(chat_id, file_cert, caption=f'Сертификаты без ссылок')

        if os.path.exists(file_cert_name):
            os.remove(file_cert_name)

        await need_example_class.insert_logging_in_db(chat_id, message_text, datetime.now(),
                                                      'Ветеринарные сертификаты')

    elif await need_example_class.get_access_section(chat_id, message_text[
                                                              2:]) and message_text == '📬 Сертификаты со ссылками':
        file_cert_name = await need_example_class.get_veterinary_certificates(chat_id, 'url')

        async with aiofiles.open(file_cert_name, 'rb') as file_cert:
            await bot.send_document(chat_id, file_cert, caption=f'Сертификаты со ссылками')

        if os.path.exists(file_cert_name):
            os.remove(file_cert_name)

        await need_example_class.insert_logging_in_db(chat_id, message_text, datetime.now(),
                                                      'Ветеринарные сертификаты')

    elif await need_example_class.get_access_section(chat_id, message_text[
                                                              2:]) and message_text == '↕️ История изменений сертификатов':
        file_cert_name = await need_example_class.get_veterinary_certificates(chat_id, 'history')

        async with aiofiles.open(file_cert_name, 'rb') as file_cert:
            await bot.send_document(chat_id, file_cert, caption=f'История изменений сертификатов')

        if os.path.exists(file_cert_name):
            os.remove(file_cert_name)

        await need_example_class.insert_logging_in_db(chat_id, message_text, datetime.now(),
                                                      'Ветеринарные сертификаты')

    elif await need_example_class.get_access_section(chat_id, message_text[
                                                              2:]) and message_text == '🔍 Запуск проверки сертификатов':
        # Параметры запуска DAG
        dag_variables = await need_example_class.get_variables_dag('Проверка_Сертификатов', chat_id)
        # Параметры интервала запуска для проверки
        timeout_value = await need_example_class.get_timeout_operation_value('Проверка_Сертификатов')

        if await need_example_class.check_timeout_operation('Проверка_Сертификатов', timeout_value['field'],
                                                            timeout_value['timeout']):
            response_dag_run = await need_example_class.trigger_dag(os.getenv('DAG_BARIER'),
                                                                    dag_variables)
            if 400 in response_dag_run:
                await bot.send_message(chat_id, response_dag_run[0] + '\nПопробуйте запустить позже')
            else:
                await bot.send_message(chat_id, '▶️ Процесс запущен')
            await need_example_class.insert_logging_in_db(chat_id, message_text, datetime.now(),
                                                          'Парсинг данных')
        else:
            await bot.send_message(chat_id, '🔄 Время повторного запуска еще не пришло')

    elif await need_example_class.get_access_section(chat_id, message_text[
                                                              2:]) and message_text == '❗️ Обзор барьеров по странам':
        await bot.send_message(chat_id, 'Для выбора страны воспользуйтесь кнопками 👇',
                               reply_markup=create_replay_markup(message_text, 'barier'))

    elif await need_example_class.get_access_section(chat_id, message_text[
                                                              2:]) and message_text == '🌍 Список стран':
        await need_example_class.update_state_user(chat_id, 'barier_country')
        list_sorted_country = sorted([i for i in os.listdir(path_barier_country) if '.' not in i])
        dict_country = {i.split()[-1].strip() if len(i.encode('utf-8')) > 63 else i.strip(): i for i in
                        list_sorted_country}

        pagination_status = await need_example_class.get_pagination_status(chat_id)
        await bot.send_message(chat_id, 'Доступные страны:', parse_mode='markdown',
                               reply_markup=create_inline_markup('barier_country', dict_country, pagination_status))

    elif await need_example_class.get_access_section(chat_id, message_text[2:]) and message_text == '🚪 В главное меню':
        await need_example_class.update_state_user(chat_id, 'main')
        await bot.send_message(chat_id, 'Вы вернулись в главное меню!', reply_markup=create_replay_markup('', 'main'))

    elif await need_example_class.get_access_section(chat_id, message_text[2:]) and message_text == '🔙 Назад':
        await bot.send_message(chat_id, 'Выберите раздел 👇', reply_markup=create_replay_markup(message_text, 'barier'))

    else:
        await bot.send_message(chat_id, '🕵🏻‍♂️ Такой команды не существует, либо у вас нет доступа, возможно, вам поможет команада /start')


@bot.callback_query_handler(
    func=lambda call: need_example_class.dct_user_state[call.message.chat.id] == 'barier_country')
async def get_barier_reference(call: types.CallbackQuery):
    """
    Функция отрабатывает, когда состояние пользователя равно 'barier_country'
    Возвращает выбранную пользователем справку по стране

    :param call: callback с инлайновой клавиатуры
    :return:
    """
    call_text = call.data
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    list_sorted_country = sorted([i for i in os.listdir(path_barier_country) if '.' not in i])
    dict_country = {i.split()[-1].strip() if len(i.encode('utf-8')) > 63 else i.strip(): i for i in list_sorted_country}

    logging.info(f"user = {chat_id}, state = {need_example_class.dct_user_state[chat_id]}, callback = {call_text}")

    # Управление пагинацией для становых справок
    if call_text in ['next', 'back'] and await need_example_class.check_user(chat_id):
        pagination_status = await need_example_class.get_pagination_status(chat_id, call_text)
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="Доступные страны:",
            parse_mode="markdown",
            reply_markup=create_inline_markup('barier_country', dict_country, pagination_status))

    # Отправляем справку пользователю
    elif call_text in dict_country and await need_example_class.check_user(chat_id):
        path_full = path_barier_country + dict_country[call_text]
        way_pah_values = Path(path_full)
        need_search = File_search(way_pah_values)
        barier_path = need_search.get_actual_barier_reference()
        await bot.delete_message(chat_id, message_id)
        if barier_path != '':
            async with aiofiles.open(barier_path, 'rb') as f_barier:
                await bot.send_document(chat_id, f_barier, caption='Последняя версия файла')
        else:
            await bot.send_message(chat_id, 'Файл отсутствует')

        await need_example_class.update_state_user(chat_id, 'barier')
        await need_example_class.insert_logging_in_db(chat_id, dict_country[call_text], datetime.now(),
                                                      'Актуальные справки тарифные/нетарифные барьеры')


@bot.message_handler(func=lambda message: need_example_class.dct_user_state[message.chat.id] == 'region')
async def region_section(message: types.Message):
    """
    Функция отвечающая за блок регионального отдела

    :param message: сообщение от пользователя
    :return:
    """
    chat_id = message.chat.id
    message_text = message.text

    logging.info(f"user = {chat_id}, state = {need_example_class.dct_user_state[chat_id]}, message = {message_text}")

    if await need_example_class.get_access_section(chat_id,
                                                   message_text[2:]) and message_text == '📜 Справки по форме 8':
        await bot.send_message(chat_id, 'Выберите название региона воспользовавшись кнопкой 💡',
                               reply_markup=create_replay_markup(message_text, 'region'))

    elif await need_example_class.get_access_section(chat_id, message_text[
                                                              2:]) and message_text == '📔 Перечень регионов':
        await need_example_class.update_state_user(chat_id, 'region_reference')
        list_sorted_region = sorted(
            [i for i in os.listdir(path_region) if '_' not in i and '.d' not in i and '.p' not in i and '.D' not in i],
            key=lambda x: x[0].lower())
        dict_name_region = {i[:20].replace(' - ', '-') if len(i.encode('utf-8')) > 63 else i.replace(' - ', '-'): i for
                            i in list_sorted_region}
        pagination_status = await need_example_class.get_pagination_status(chat_id)
        await bot.send_message(chat_id, 'Доступные регионы:', parse_mode='markdown',
                               reply_markup=create_inline_markup('region_reference', dict_name_region,
                                                                 pagination_status))

    elif await need_example_class.get_access_section(chat_id, message_text[2:]) and message_text == '🔙 Назад':
        await bot.send_message(chat_id, 'Выберите раздел 👇', reply_markup=create_replay_markup(message_text, 'region'))

    elif await need_example_class.get_access_section(chat_id, message_text[2:]) and message_text == '🚪 В главное меню':
        await need_example_class.update_state_user(chat_id, 'main')
        await bot.send_message(chat_id, 'Вы вернулись в главное меню!', reply_markup=create_replay_markup('', 'main'))

    else:
        await bot.send_message(chat_id, '🕵🏻‍♂️ Такой команды не существует, либо у вас нет доступа, возможно, вам поможет команада /start')


@bot.callback_query_handler(
    func=lambda call: need_example_class.dct_user_state[call.message.chat.id] == 'region_reference')
async def get_region_reference(call: types.CallbackQuery):
    """
    Функция отрабатывает, когда состояние пользователя равно 'region_reference'
    Возвращает выбранную пользователем справку по региону

    :param call: callback с инлайновой клавиатуры
    :return:
    """
    call_text = call.data
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    list_sorted_region = sorted(
        [i for i in os.listdir(path_region) if '_' not in i and '.d' not in i and '.p' not in i and '.D' not in i],
        key=lambda x: x[0].lower())
    dict_name_region = {i[:20].replace(' - ', '-') if len(i.encode('utf-8')) > 63 else i.replace(' - ', '-'): i for i in
                        list_sorted_region}

    logging.info(f"user = {chat_id}, state = {need_example_class.dct_user_state[chat_id]}, callback = {call_text}")

    # Управление пагинацией для становых справок
    if call_text in ['next', 'back'] and await need_example_class.check_user(chat_id):
        pagination_status = await need_example_class.get_pagination_status(chat_id, call_text)
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="Доступные регионы:",
            parse_mode="markdown",
            reply_markup=create_inline_markup('region_reference', dict_name_region, pagination_status))

    # Отправляем справки по форме 1,2 пользователю
    elif call_text in dict_name_region and await need_example_class.check_user(chat_id):
        path_full = path_region + dict_name_region[call_text]
        way_pah_values = Path(path_full)
        need_search = File_search(way_pah_values)
        region_path = need_search.get_actual_region_reference()
        await bot.delete_message(chat_id, message_id)
        if region_path != '':
            async with aiofiles.open(region_path, 'rb') as f_barier:
                await bot.send_document(chat_id, f_barier, caption='Последняя версия файла')
        else:
            await bot.send_message(chat_id, 'Файл отсутствует')

        await need_example_class.update_state_user(chat_id, 'region')
        await need_example_class.insert_logging_in_db(chat_id, dict_name_region[call_text], datetime.now(),
                                                      'Актуальные региональные справки')


@bot.callback_query_handler(func=lambda call: need_example_class.dct_user_state[call.message.chat.id] == 'subscribe')
async def get_subscribe(call: types.CallbackQuery):
    """
    Функция отрабатывает, когда состояние пользователя равно 'subscribe'
    Отвечает за управление алертами (подписка на них или отписка)

    :param call: callback с инлайновой клавиатуры
    :return:
    """
    call_text = call.data
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    logging.info(f"user = {chat_id}, state = {need_example_class.dct_user_state[chat_id]}, callback = {call_text}")

    if await need_example_class.check_user(chat_id):
        # Навигация по доступным алертам
        if call_text in ['next', 'back']:
            pagination_status = await need_example_class.get_pagination_status(chat_id, call_text)
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                        text='Выберите рассылку, статус которой хотите изменить 📨',
                                        reply_markup=create_inline_markup(state='subscribe',
                                                                          list_itemns=await need_example_class.get_alert_description(
                                                                              chat_id),
                                                                          pagen=pagination_status,
                                                                          element_on_page=5))

        # Если пользователь выбирает изменение состояния алерта
        elif call_text.isdigit():
            btn_text = [j['text'] for i in call.message.json['reply_markup']['inline_keyboard'] for j in i if
                        j['callback_data'] == call_text][0]
            await bot.delete_message(chat_id, message_id)
            await need_example_class.update_state_user(chat_id, 'main')
            await need_example_class.alert_status_update(chat_id, int(call_text))
            await bot.send_message(chat_id,
                                   f"""Вы успешно {'<b>отписались</b> от рассылки' if '✅' in btn_text else '<b>подписались</b> на рассылку'} 
                                            \n"<b>{btn_text[2:]}</b>\"""",
                                   reply_markup=create_replay_markup('', 'main'),
                                   parse_mode='html')

        # Если пользователь ничего не выбрал, то может без изменений перейти в главное меню
        elif call_text == 'main':
            await bot.delete_message(chat_id, message_id)
            await need_example_class.update_state_user(chat_id, 'main')
            await bot.send_message(chat_id, 'Вы вернулись в главное меню!',
                                   reply_markup=create_replay_markup('', 'main'))
    else:
        await bot.send_message(chat_id=chat_id, text='👻')

if __name__ == '__main__':
    asyncio.run(bot.infinity_polling(logger_level=10))
