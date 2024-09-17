import os
from datetime import datetime
import re
import pathlib


class File_search:
    """
    Клас отвечающий за поиск файлов по переданному пути
    :param way_pah_values: путь к нужной дирректории или файлу
    :type way_pah_values: pathlib.WindowsPath

    :param list_patern_forma2: паттерны поиска файлов для справок формы 2
    :type list_patern_forma2: list

    :param list_patern_forma1_docx: паттерны поиска файлов .docx для справок формы 1
    :type list_patern_forma1_docx: list

    :param list_patern_forma1_xlsx: паттерны поиска файлов .xlsx для справок формы 1
    :type list_patern_forma1_xlsx: list

    :param list_patern_barier: паттерны поиска файлов для справок отдела Барьеров
    :type list_patern_barier: list

    :param list_patern_region: паттерны поиска файлов для справок отдела Регионов
    :type list_patern_region: list
    """
    def __init__(self, way_pah_values: pathlib.Path):
        self.way_pah_values = way_pah_values
        self.list_patern_forma2 = ['**/*форма2,*.docx', '**/*форма 2,*.docx', '**/*форма_2,*.docx']
        self.list_patern_forma1_docx = ['**/*форма1,*.docx', '**/*форма 1,*.docx', '**/*форма_1,*.docx']
        self.list_patern_forma1_xlsx = ['**/*форма 1,*.xlsx', '**/*форма1,*.xlsx', '**/*форма_1,*.xlsx']
        self.list_patern_barier = ["**/*-* на *.docx"]
        self.list_patern_region = ["**/*.*.docx"]

    def get_actual_form2(self) -> pathlib.WindowsPath:
        """
        Для управления Внешней торговли
        Функция возвращает справку по форме 2 с самой поздней датой редактирования

        :return: путь к файлу
        """
        temp_path_f2 = ''
        temp_date_f2 = ''
        count_f2 = 0
        for patern in self.list_patern_forma2:
            if len(list(self.way_pah_values.glob(patern))) > 0:
                for i in self.way_pah_values.glob(patern):
                    if count_f2 == 0:
                        temp_path_f2 = i
                        temp_date_f2 = os.path.getctime(i)
                    elif temp_date_f2 < os.path.getctime(i):
                        temp_date_f2 = os.path.getctime(i)
                        temp_path_f2 = i
                    count_f2 += 1
        return temp_path_f2

    def get_actual_form1(self) -> list[pathlib.WindowsPath]:
        """
        Для управления Внешней торговли
        Функция возвращает справки по форме 1 с самой поздней датой редактирования

        :return: путь к файлам
        """
        temp_path_f1 = ''
        temp_date_f1 = ''
        count_f1 = 0
        temp_path_exl = ''
        temp_date_exl = ''
        count_exl = 0
        for docx in self.list_patern_forma1_docx:
            if len(list(self.way_pah_values.glob(docx))) > 0:
                for d in self.way_pah_values.glob(docx):
                    if count_f1 == 0:
                        temp_path_f1 = d
                        temp_date_f1 = os.path.getctime(d)
                    elif temp_date_f1 < os.path.getctime(d):
                        temp_date_f1 = os.path.getctime(d)
                        temp_path_f1 = d
                    count_f1 += 1

        for xlsx in self.list_patern_forma1_xlsx:
            if len(list(self.way_pah_values.glob(xlsx))) > 0:
                for x in self.way_pah_values.glob(xlsx):
                    if count_exl == 0:
                        temp_path_exl = x
                        temp_date_exl = os.path.getctime(x)
                    elif temp_date_exl < os.path.getctime(x):
                        temp_date_exl = os.path.getctime(x)
                        temp_path_exl = x
                    count_exl += 1
        return [temp_path_f1, temp_path_exl]

    def get_date_create_form2(self) -> list[str]:
        """
        Для управления Внешней торговли
        Функция возвращающая даты на которые были сделаны справки по форме 2

        :return: список дат указанных в названии справок
        """
        dict_date_form2 = {}
        for way_path_file in self.way_pah_values.glob("**/*форм*2,*.doc*"):
            try:
                date_form2 = re.search(r'\d\d\d\d[._]\d\d[._]\d\d', str(way_path_file))[0]
                date_form2_replace = date_form2.replace('.', '').replace('_', '')
                if date_form2_replace in dict_date_form2:
                    dict_date_form2[date_form2_replace] = date_form2 if '.' in date_form2 else dict_date_form2[date_form2_replace]
                else:
                    dict_date_form2[date_form2_replace] = date_form2
            except TypeError:
                print(way_path_file)
        return sorted([v for k, v in dict_date_form2.items()], reverse=True)

    def get_need_version_form2(self, date_form2: str) -> pathlib.WindowsPath:
        """
        Для управления Внешней торговли
        Функция возвращает справку по форме 2 на указанную дату

        :param date_form2: дата указанная в названии справки
        :return: путь к нужной справке
        """
        for form in self.way_pah_values.glob('**/*форм*2,*.doc*'):
            if date_form2 in str(form):
                return form

    def get_date_create_form1(self) -> list[str]:
        """
        Для управления Внешней торговли
        Функция возвращающая даты на которые были сделаны справки по форме 1
        поиск идет только среди справок с расширением .doc

        :return: список дат указанных в названии справок
        """
        dict_date_form1 = {}
        for way_path_file in self.way_pah_values.glob("**/*форм*1,*.doc*"):
            try:
                date_form1 = re.search(r'\d\d\d\d[._]\d\d[._]\d\d', str(way_path_file))[0]
                date_form1_replace = date_form1.replace('.', '').replace('_', '')
                if date_form1_replace in dict_date_form1:
                    dict_date_form1[date_form1_replace] = date_form1 if '.' in date_form1 else dict_date_form1[
                        date_form1_replace]
                else:
                    dict_date_form1[date_form1_replace] = date_form1
            except TypeError:
                print(way_path_file)
        return sorted([v for k, v in dict_date_form1.items()], reverse=True)

    def get_need_version_form1(self, date_form1: str) -> list[pathlib.WindowsPath]:
        """
        Для управления Внешней торговли
        Функция возвращает справки по форме 1 на указанную дату

        :param date_form1: дата указанная в названии справки
        :return: список путей к нужным справкам
        """
        for form_doc in self.way_pah_values.glob('**/*форм*1,*.doc*'):
            if date_form1 in str(form_doc):
                forma1_doc = form_doc
                break

        for form_x in self.way_pah_values.glob('**/*форм*1,*.xls*'):
            if date_form1 in str(form_x):
                return [forma1_doc, form_x]

    def get_actual_barier_reference(self) -> pathlib.WindowsPath:
        """
        Для отдела Барьеров
        Функция отбирает самую актульную справку по дате указанной в ее названии

        :return: дату актульной справки
        """
        need_path_barier = ''
        need_date_barier = ''
        count_barier = 0

        for patern in self.list_patern_barier:
            if len(list(self.way_pah_values.glob(patern))) > 0:
                for i in self.way_pah_values.glob(patern):
                    if '~$' not in str(i):
                        date_tmp = datetime.strptime(re.search(r'\d\d[._]\d\d[._]\d\d\d\d', str(i))[0], '%d.%m.%Y')
                        if count_barier == 0:
                            need_path_barier = i
                            need_date_barier = date_tmp
                        elif need_date_barier < date_tmp:
                            need_date_barier = date_tmp
                            need_path_barier = i
                        count_barier += 1
        return need_path_barier

    def get_actual_region_reference(self) -> pathlib.WindowsPath:
        """
        Для отдела Регионов
        Функция отбирает самую актульную справку по дате указанной в ее названии

        :return: дату актульной справки
        """
        need_path_region = ''
        need_date_region = ''
        count_region = 0

        for patern in self.list_patern_region:
            if len(list(self.way_pah_values.glob(patern))) > 0:
                for i in self.way_pah_values.glob(patern):

                    date_tmp = datetime.strptime(re.search(r'\d\d[._]\d\d[._]\d\d\d\d', str(i))[0], '%d.%m.%Y')
                    if count_region == 0:
                        need_path_region = i
                        need_date_region = date_tmp
                    elif need_date_region < date_tmp:
                        need_date_region = date_tmp
                        need_path_region = i
                    count_region += 1
        return need_path_region

