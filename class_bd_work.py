from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
import os
from dotenv import load_dotenv
import asyncpg
from asyncpg.pool import Pool
import datetime
import pandas as pd
import requests
import logging
import json

if os.path.exists('.env'):
    load_dotenv('.env')


class Hepl_work_by_postgre:
    """
    Класс риализующий дополнительную логику работы с базой данных пользователей ТГ бота

    :param alch_pg: не асинхронное соединение с БД Postgres
    :type alch_pg: Engine

    :param dct_user_state: словарь собираемый в момент инициализации экземпляра класса
                           и необходимый для проверки состояния пользователей
    :type dct_user_state: dict

    :param pool_aeforecast: пул асинхронных соединений для работы с бд Postgre Агроэкспорт
    :type pool_aeforecast: Pool | null

    :param pool_masterhost: пул асинхронных соединений для работы с бд Postgre masterhost
    :type pool_masterhost: Pool | null

    :param list_nnnn_country: картеж стран, которые мы не показываем для пользователей со стастусом не admin
    :type list_nnnn_country: typle
    """

    def __init__(self):
        self.alch_pg = create_engine(
            f"postgresql://{os.getenv('USER_NAME_PG')}:{os.getenv('PASSWORD_PG')}@{os.getenv('HOST_PG')}:{os.getenv('PORT_PG')}/{os.getenv('DATABASE_PG')}")
        self.dct_user_state = self.create_dct()
        self.pool_aeforecast = None
        self.pool_masterhost = None
        self.list_nnnn_country = {'Венесуэла', 'Иран', 'Куба', 'Сирия'}

    def create_dct(self) -> dict:
        """
        Возвращает словарь состояний каждого из пользователей
        необходимо для валидации состояния в callback_query_handler

        :return: словарь состояний пользователей
        """
        df_state = pd.read_sql("""SELECT * FROM bot.state_user""", con=self.alch_pg)
        return {k: v for k, v in zip(df_state.chat_id.tolist(), df_state.current_state.tolist())}

    async def create_pool(self):
        """
        Создает асинхронный пул соединений для баз данных.
        Если такие еще не были созданы
        """
        if self.pool_aeforecast is None:
            self.pool_aeforecast = await asyncpg.create_pool(user=os.getenv('USER_NAME_PG'),
                                                             password=os.getenv('PASSWORD_PG'),
                                                             host=os.getenv('HOST_PG'),
                                                             port=os.getenv('PORT_PG'),
                                                             database=os.getenv('DATABASE_PG'), max_size=2, min_size=1)
        else:
            pass
        if self.pool_masterhost is None:
            self.pool_masterhost = await asyncpg.create_pool(user=os.getenv('USER_NAME_MH'),
                                                             password=os.getenv('PASSWORD_MH'),
                                                             host=os.getenv('HOST_MH'),
                                                             port=os.getenv('PORT_MH'),
                                                             database=os.getenv('DATABASE_MH'), max_size=2, min_size=1)
        else:
            pass

    @staticmethod
    async def write_hello_func() -> str:
        """
        Рассчитывает приветственную фразу в зависимости от текущего времени
        :return: строку приветствия
        """
        hour = datetime.datetime.now().hour
        if 1 < hour <= 9:
            return 'Доброе утро'
        elif 9 < hour <= 13:
            return 'Добрый день'
        elif 13 < hour <= 20:
            return 'Добрый вечер'
        elif 20 <= hour <= 1:
            return 'Доброй ночи'

    async def check_user(self, user_id: int, flag_approv: str = 'full') -> bool:
        """
        Проверяет 3 состояния пользователя
        - Есть в базе и авторизован
        - Есть в базе, но не авторизован (отсутствует токен)
        - Нет вообще в базе

        :param user_id: chat_id пользователя

        :param flag_approv: флаг, в зависимости от значения которого проверяется частный случай

        :return: True or False
        """
        await self.create_pool()

        async with self.pool_aeforecast.acquire() as conn:
            if flag_approv == 'full':
                return await conn.fetchval(
                    """SELECT EXISTS(SELECT 1 
                       FROM bot.user_tg_bot 
                       WHERE chat_id = $1 
                       AND uu_user_id IS NOT NULL
                       AND active_user)""",
                    user_id)

            elif flag_approv == 'not_token':
                return await conn.fetchval(
                    """SELECT EXISTS(SELECT 1 
                       FROM bot.user_tg_bot 
                       WHERE chat_id = $1 
                       AND uu_user_id IS NULL
                       AND active_user)""",
                    user_id)
            elif flag_approv == 'not_active':
                return await conn.fetchval(
                    """SELECT EXISTS(SELECT 1 
                       FROM bot.user_tg_bot 
                       WHERE chat_id = $1 
                       AND uu_user_id IS NOT NULL
                       AND NOT active_user)""",
                    user_id)
            else:
                return await conn.fetchval("""SELECT EXISTS(SELECT 1 
                                              FROM bot.user_tg_bot 
                                              WHERE chat_id = $1
                                              AND active_user)""",
                                           user_id)

    async def update_state_user(self, user_id: int, state: str):
        """
        Обновляет состояние пользователя в БД и словаре

        :param user_id: chat_id пользователя

        :param state: состояние в котором будет находиться пользователь
        """
        await self.create_pool()
        async with self.pool_aeforecast.acquire() as conn:
            await conn.execute(
                """UPDATE bot.state_user SET previous_state = current_state, current_state = $1 WHERE chat_id = $2""",
                state, user_id)
        self.dct_user_state[user_id] = state

    async def get_current_state(self, user_id: int) -> str:
        """

        :param user_id: chat_id пользователя

        :return: текущее состояние пользователя записанное в БД
        """
        await self.create_pool()
        async with self.pool_aeforecast.acquire() as conn:
            return await conn.fetchval("""SELECT current_state FROM bot.state_user WHERE chat_id = $1""", user_id)

    async def get_previous_state(self, user_id: int) -> str:
        """

        :param user_id: chat_id пользователя

        :return: предыдущее состояние пользователя записанное в БД
        """
        async with self.pool_aeforecast.acquire() as conn:
            return await conn.fetchval("""SELECT previous_state FROM bot.state_user WHERE chat_id = $1""", user_id)

    async def add_user_in_db(self, user_id: int):
        """
        Добавляет нового пользоватеоя в БД без токина и с ролью user

        :param user_id: chat_id пользователя
        """
        async with self.pool_aeforecast.acquire() as conn:
            await conn.execute("""INSERT INTO bot.user_tg_bot(chat_id, role_id, active_user) VALUES ($1, 1, True)""", user_id)

    async def validate_token(self, token: str, id_service: str) -> bool:
        """
        Проверяет есть ли такой токен в поле токны БД masterhost
        И провермят нет ли такого токена в БД Агроэкспорт у уже записанных пользователей

        :param token: токен(uuid) пользователя полученный им при регистрации на сайте организации

        :param id_service: id сервиса в котором валидируем пользователя

        :return: True or False
        """
        await self.create_pool()
        async with self.pool_masterhost.acquire() as conn_mh:
            try:
                mh_bool = await conn_mh.fetchval("""SELECT EXISTS(SELECT 1 FROM bot.service_access WHERE user_id = $1 AND service_id = $2)""",
                                                 token, id_service)
            except:
                logging.exception('Не верный токен')
                mh_bool = False

        async with self.pool_aeforecast.acquire() as conn:
            ae_bool = await conn.fetchval("""SELECT COUNT(*) = 0 FROM bot.user_tg_bot WHERE uu_user_id = $1""",
                                          token)

        return mh_bool and ae_bool

    async def update_token_user(self, user_id: int, token: str):
        """
        Обновляет токен переданные не авторизованным пользователем

        :param user_id: chat_id пользователя

        :param token: токен(uuid) пользователя полученный им при регистрации на сайте организации
        """
        async with self.pool_aeforecast.acquire() as conn:
            await conn.execute("""UPDATE bot.user_tg_bot SET uu_user_id = $1 WHERE chat_id = $2""", token, user_id)

    async def get_access_section(self, user_id: int, message_text: str) -> bool:
        """
        Провермяем есть указанные раздел в доступе у роли, которой наделен пользователь

        :param user_id: chat_id пользователя

        :param message_text: текст сообщения пользователя (наименование раздела в боте)

        :return: True or False
        """
        if len(message_text) == 0:
            return False
        await self.create_pool()
        async with self.pool_aeforecast.acquire() as conn:
            return await conn.fetchval("""SELECT EXISTS(SELECT 1 FROM bot.role_table 
                    WHERE role_id = (SELECT role_id FROM bot.user_tg_bot WHERE chat_id = $1) AND button_names LIKE('%' || $2 || '%'))""",
                                       user_id, message_text)

    async def get_pagination_status(self, user_id: int, status: str = 'default') -> int:
        """
        Возвращает пагинацию клавиатуры для указанного пользователя в зависимости от переданного статуса
        - default: пользователь на первой страницу
        - next: итерируется дальше по списку страниц
        - back: итерируется к началу по списку страниц

        :param user_id: chat_id пользователя

        :param status: положение, куда двигается пользователь или только начинает работу с клавитатурой
                       (default)

        :return: номер страницы
        """
        await self.create_pool()
        if status == 'default':
            async with self.pool_aeforecast.acquire() as conn:
                await conn.execute(
                    """UPDATE bot.pagination_status SET status_user_for_page = 0 WHERE chat_id = $1""", user_id)
                return 0
        elif status == 'next':
            async with self.pool_aeforecast.acquire() as conn:
                pagen = await conn.fetchval(
                    """SELECT status_user_for_page FROM bot.pagination_status WHERE chat_id = $1""", user_id)
                pagen += 1
                await conn.execute(
                    """UPDATE bot.pagination_status SET status_user_for_page = $2 WHERE chat_id = $1""", user_id,
                    pagen)
                return pagen
        elif status == 'back':
            async with self.pool_aeforecast.acquire() as conn:
                pagen = await conn.fetchval(
                    """SELECT status_user_for_page FROM bot.pagination_status WHERE chat_id = $1""", user_id)
                pagen = 0 if pagen == 0 else pagen - 1
                await conn.execute(
                    """UPDATE bot.pagination_status SET status_user_for_page = $2 WHERE chat_id = $1""", user_id,
                    pagen)
                return pagen

    async def check_roll_user(self, user_id: int) -> str:
        """

        :param user_id: chat_id пользователя

        :return: роль пользователя в БД
        """
        await self.create_pool()
        async with self.pool_aeforecast.acquire() as conn:
            return await conn.fetchval("""SELECT role_id FROM bot.user_tg_bot WHERE chat_id = $1""", user_id)

    async def filter_country_nnn(self, user_id: int, country_list: list) -> list[str]:
        """
        Отбираем необходимые станы в зависимоти от того, какая роль у пользователя

        :param user_id: chat_id пользователя

        :param country_list: список переданных стран

        :return: отсортированный список доступных стран
        """
        clear_country_list = [i for i in country_list if '_' not in i and '.' not in i]
        if await self.check_roll_user(user_id) in (2, 4):
            return sorted(clear_country_list)
        else:
            return sorted(list(set(clear_country_list) - self.list_nnnn_country))

    async def update_section_bot(self, user_id: int, country: str):
        """
        Обновляет название страны, скоторой крайний раз взаимодействовал пользователь

        :param user_id: chat_id пользователя

        :param country: назване страны
        """
        await self.create_pool()
        async with self.pool_aeforecast.acquire() as conn:
            await conn.execute("""UPDATE bot.pagination_status SET section_bot = $2 WHERE chat_id = $1""",
                               user_id, country)

    async def get_section_bot(self, user_id: int) -> str:
        """

        :param user_id: chat_id пользователя

        :return: секцию(страну) с которой взаимодействовал пользователь
        """
        await self.create_pool()
        async with self.pool_aeforecast.acquire() as conn:
            return await conn.fetchval("""SELECT section_bot FROM bot.pagination_status WHERE chat_id = $1""",
                                       user_id)

    async def insert_logging_in_db(self, user_id: int, name_button: str,
                                   time_operation: datetime.datetime, menu_section: str):
        """
        Логируем целевое действие пользователей
        Такие как:
        - получение справок
        - сертификатов
        - запуск etl процессов

        :param user_id: chat_id пользователя

        :param name_button: наименование кнопки, которая привела к целевому действие

        :param time_operation: время совершения операции

        :param menu_section: раздел, к которому относится кнопка
        """
        await self.create_pool()
        async with self.pool_aeforecast.acquire() as conn:
            await conn.execute("""INSERT INTO bot.logging_table_by_click_button VALUES ($1, $2, $3, $4)""", user_id,
                               name_button,
                               time_operation, menu_section)

    async def get_veterinary_certificates(self, user_id: int, flag_type_file_data: str) -> str:
        """
        Возвращает перечень ветеринарных сертификатов в зависимоти от переданного флага
        - not_url: сертефикаты без ссылок
        - url: сертефикаты с сылками
        - history: история изменения сертификатов

        :param user_id: chat_id пользователя

        :param flag_type_file_data: флаг, в зависимости от которого будет выбран sql скрипт

        :return: наименование созданного файла
        """

        name_file_cert = f'Ветеринарные сертификаты {user_id}.xlsx'
        if flag_type_file_data == 'not_url':
            sql_cert = """SELECT certificat_name, document_number, period, country 
                          FROM airflow.veterinary_certificates
                          WHERE version_update = 'new'
                          ORDER BY country"""
        elif flag_type_file_data == 'url':
            sql_cert = """SELECT certificat_name, document_number, period, country, url_certificat 
                          FROM airflow.veterinary_certificates
                          WHERE version_update = 'new'
                          ORDER BY country"""
        elif flag_type_file_data == 'history':
            sql_cert = """SELECT certificat_name, document_number, period, 
                            country, url_certificat,
                            date_update :: date, version_update
                          FROM airflow.change_history_certificates
                          ORDER BY country"""

        df_cert = pd.read_sql(sql_cert, con=self.alch_pg)
        df_cert['certificat_name'] = df_cert['certificat_name'].apply(lambda x: x[0])
        with pd.ExcelWriter(name_file_cert, engine='xlsxwriter') as writer:
            df_cert.to_excel(writer, sheet_name='Сертификаты', index=False, na_rep='NaN')
            for column in df_cert:
                column_width = max(df_cert[column].astype(str).map(len).max(), len(column))
                col_idx = df_cert.columns.get_loc(column)
                writer.sheets['Сертификаты'].set_column(col_idx, col_idx,
                                                        len(column) + 10 if column_width > 200 else column_width)
            writer.sheets['Сертификаты'].set_default_row(30)
        return name_file_cert

    async def check_timeout_operation(self, operation_name: str, field: str, timeout: int) -> bool:
        """
        Проверяем, прошел ли тайм-аут на переданной операции

        :param operation_name: наименоване операции (пример, Проверка_Сертификатов)

        :param field: какую часть из времени мы вытаскиваем (day, hour, minute и тд.)

        :param timeout: сколько должно было пройти времени с момента последнего запуска операции

        :return: True or False
        """

        async with self.pool_aeforecast.acquire() as conn:
            value = await conn.fetchval("""SELECT CASE 
                                        WHEN $2 = 'day' 
                                            THEN DATE_PART($2, NOW() - timeout_operation) >= $3
                                        WHEN $2 = 'hour'
                                            THEN (DATE_PART($2, NOW() - timeout_operation) + DATE_PART('day', NOW() - timeout_operation) * 24) >= $3
                                        WHEN $2 = 'minute'
                                            THEN (DATE_PART($2, NOW() - timeout_operation) + DATE_PART('hour', NOW() - timeout_operation) * 60 + DATE_PART('day', NOW() - timeout_operation) * 1440) >= $3
                                        END
                                        FROM bot.status_operation 
                                        WHERE operation_name = $1""", operation_name, field, timeout)
            return True if value is None else value

    @staticmethod
    async def trigger_dag(dag_id: str, json_conf: dict) -> list[str | int]:
        """
        Триггер DAG, id которого был передан

        :param dag_id: id DAG, который будет запускать в ручную

        :param json_conf: набор параметров для конкретного DAG

        :return: список с состоянием, удачно был запущен DAG или что-то пошло не так
        """

        head = {'Content-Type': 'application/json'}
        json_conf = {'conf': json_conf}
        response_json = requests.post(os.getenv('TRIGGER_URL').format(dag_id=dag_id),
                                      auth=(os.getenv('AIRFLOW_USER'), os.getenv('AIRFLOW_PASSWORD')), headers=head,
                                      json=json_conf).json()

        if 'status' in response_json:
            return [response_json['detail'], response_json['status']]
        else:
            return [response_json['run_type']]

    async def get_alert_description(self, user_id: int) -> list[dict]:
        """
        Пример возвращаемых данных:
            [{'alert_id': 2, 'type_alert': 'Обновление данных в БД', 'status_alert': True},
             {'alert_id': 1, 'type_alert': 'Ветеринарные сертификаты', 'status_alert': True}]

        :param user_id: chat_id пользователя

        :return: список словарей с необходимой информацией для каждого пользователя
        """
        await self.create_pool()
        async with self.pool_aeforecast.acquire() as conn:
            query_result = await conn.fetch("""SELECT alert_id, type_alert, status_alert 
                                          FROM bot.alert_status 
                                          JOIN bot.alert_type_table USING(alert_id)
                                          WHERE chat_id = $1""", user_id)

        return [dict(row) for row in query_result]

    async def alert_status_update(self, user_id: int, alert_id: int):
        """
        Меняет статус алерта на противположные:
        Пользователь был подписан на алерт(True), выбрал соответствующую кнопку и изменил свой статус на отписан(False)

        :param user_id: chat_id пользователя

        :param alert_id: идентификатор нужного алерта

        :return:
        """
        async with self.pool_aeforecast.acquire() as conn:
            await conn.execute(
                f"""UPDATE bot.alert_status 
                   SET status_alert = CASE WHEN status_alert = True THEN False ELSE True END 
                   WHERE alert_id = $1 AND chat_id = $2""", alert_id, user_id)

    async def get_variables_dag(self, operation_name: str, user_id: int) -> dict:
        """
        :param operation_name: выбранный пользователем DAG

        :param user_id: chat_id пользователя

        :return: сформированный словарь параметров для запуска DAG
        """
        async with self.pool_aeforecast.acquire() as conn:
            await conn.set_type_codec(
                'json',
                encoder=json.dumps,
                decoder=json.loads,
                schema='pg_catalog'
            )

            dict_variables = await conn.fetchval("""SELECT variables_dag::json 
                                          FROM bot.status_operation 
                                          WHERE operation_name = $1""", operation_name)

        # Для отправки сообщения конкретному пользователю
        if 'chat_id' in dict_variables:
            dict_variables['chat_id'] = user_id
        return dict_variables

    async def get_timeout_operation_value(self, operation_name: str) -> dict:
        """
        :param operation_name: выбранный пользователем DAG

        :return: словарь с параметрами timeout триггера DAG
        """
        async with self.pool_aeforecast.acquire() as conn:
            await conn.set_type_codec(
                'json',
                encoder=json.dumps,
                decoder=json.loads,
                schema='pg_catalog'
            )

            return await conn.fetchval("""SELECT timeout_operation_value::json
                                          FROM bot.status_operation 
                                          WHERE operation_name = $1""", operation_name)