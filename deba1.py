import pymysql.cursors

# Параметры подключения
host = 'localhost'
user = 'dev'
password = '1234'
database = 'recruiting'

try:
    # Подключаемся к базе данных
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        cursorclass=pymysql.cursors.DictCursor
    )
    print("Подключение успешно!")

except pymysql.MySQLError as e:
    print("Ошибка подключения:", e)

finally:
    # Закрываем подключение, если оно было установлено
    if 'connection' in locals() and connection.open:
        connection.close()
        print("Подключение закрыто.")
