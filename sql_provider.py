import os

class SQLProvider:
    def __init__(self, folder_path):
        """
        Инициализация SQLProvider с указанием пути к папке с SQL-запросами.
        
        :param folder_path: Путь к папке, где хранятся SQL-запросы для конкретного модуля.
        """
        if not os.path.exists(folder_path):
            raise ValueError(f"Указанная папка не существует: {folder_path}")
        self.folder_path = folder_path
    
    def get(self, file_name, **kwargs):
        """
        Возвращает SQL-запрос из файла с учётом подстановки параметров.
        
        :param file_name: Имя файла с SQL-запросом (например, "select_user.sql")
        :param kwargs: Параметры для форматирования запроса
        :return: Отформатированный SQL-запрос
        """
        file_path = os.path.join(self.folder_path, file_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл SQL-запроса не найден: {file_name}")
        
        with open(file_path, 'r', encoding='utf-8') as file:
            sql = file.read()
        
        if kwargs:
            try:
                sql = sql.format(**kwargs)
            except KeyError as e:
                raise ValueError(f"Ошибка подстановки параметра: {e}")
        
        return sql
