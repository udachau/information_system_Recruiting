import mysql.connector


class UseDatabase:                          # класс контекстного менеджера

    def __init__(self, config: dict):
        self.configuration = config

    def __enter__(self):                    # результат будет записан в часть as
        self.conn = mysql.connector.connect(**self.configuration)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
