import pymysql


class UseDatabase:
    def __init__(self, config: dict):
        self.configuration = config

    def __enter__(self):
        self.conn = pymysql.connect(**self.configuration)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
