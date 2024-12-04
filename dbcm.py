import pymysql

class UseDatabase:
    def __init__(self, config: dict):
        self.configuration = config

    def __enter__(self):
        # Приведение пароля к строке, если это необходимо
        if "password" in self.configuration and not isinstance(self.configuration["password"], str):
            self.configuration["password"] = str(self.configuration["password"])

        try:
            self.conn = pymysql.connect(**self.configuration)
            self.cursor = self.conn.cursor()
            return self.cursor
        except pymysql.MySQLError as e:
            print("Error connecting to the database:", e)
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, 'cursor') and self.cursor:
            self.cursor.close()
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
