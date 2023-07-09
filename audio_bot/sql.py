import pymysql.cursors
from main import host, user, password, db_name

con = pymysql.connect(
        host=host,
        user=user,
        port=3306,
        password=password,
        database=db_name,
        cursorclass=pymysql.cursors.DictCursor
    )


def connect_db(chat_id):
    with con.cursor() as curs:
        prob = "SELECT name_genre FROM user"
        curs.execute(prob)
        if chat_id not in [int(i['name_genre']) for i in curs.fetchall()]:
            create = "INSERT INTO user(name_genre)" \
                     f"VALUES ({chat_id})"
            curs.execute(create)
            con.commit()


def check_playlist(chat_id):
    with con.cursor() as curs:
        curs.execute("SELECT name_genre FROM playlist "
                     f"WHERE user_id LIKE (SELECT id FROM user WHERE name_genre LIKE {chat_id})")
        return [i['name_genre'] for i in curs.fetchall()]


def create_playlist(chat_id, name_playlist):
    connect_db(chat_id)
    with con.cursor() as curs:
        curs.execute("SELECT name_genre FROM playlist "
                     f"WHERE user_id LIKE (SELECT id FROM user WHERE name_genre LIKE {chat_id})")
        if name_playlist not in check_playlist(chat_id):
            create = "INSERT INTO playlist(user_id, name_genre) " \
                     f"VALUES ((SELECT id FROM user WHERE name_genre LIKE {chat_id}), '{name_playlist}')"
            curs.execute(create)
            con.commit()
            return f"Створено плейлист: {name_playlist}"
        else:
            return 'Плейлист з такою назвою вже існує'


def supplement_trak(chat_id, name_playlist, name_trak, id_trak):
    with con.cursor() as curs:
        curs.execute("INSERT INTO trak (playlist_id, name_trak, id_trak)"
                     "VALUES ((SELECT id FROM playlist "
                     f"WHERE user_id LIKE (SELECT id FROM user WHERE name_genre LIKE {chat_id}) AND "
                     f"name_genre LIKE '{name_playlist}'), '{name_trak}', '{id_trak}')")
        con.commit()


def listen_playlist(chat_id, name_playlist):
    with con.cursor() as curs:
        curs.execute("SELECT id_trak FROM trak WHERE playlist_id LIKE "
                     f"(SELECT id FROM playlist WHERE name_genre LIKE '{name_playlist}' AND user_id LIKE "
                     f"(SELECT id FROM user WHERE name_genre LIKE '{chat_id}'))")
    return [i['id_trak'] for i in curs.fetchall()]


def trak_in_playlist(chat_id, name_playlist):
    with con.cursor() as curs:
        curs.execute("SELECT id, name_trak FROM trak WHERE playlist_id LIKE "
                     f"(SELECT id FROM playlist WHERE name_genre LIKE '{name_playlist}' AND user_id LIKE "
                     f"(SELECT id FROM user WHERE name_genre LIKE '{chat_id}'))")
    return curs.fetchall()


def delete_playlist(chat_id, name_playlist):
    with con.cursor() as curs:
        curs.execute(f"DELETE FROM playlist WHERE name_genre LIKE '{name_playlist}' AND user_id LIKE "
                     f"(SELECT id FROM user WHERE name_genre LIKE '{chat_id}')")
        con.commit()
        return f'Ви видалили плейлист: <u><b>{name_playlist}</b></u>'


def delete_trak(chat_id, name_playlist, name_trak):
    with con.cursor() as curs:
        curs.execute(f"DELETE FROM trak WHERE name_trak LIKE '{name_trak}' AND playlist_id LIKE "
                     f"(SELECT id FROM playlist WHERE name_genre LIKE '{name_playlist}' AND "
                     f"user_id LIKE (SELECT id FROM user WHERE name_genre LIKE '{chat_id}'))")
        con.commit()
        return f"Ви видалили трек <b>{name_trak}</b> в плейлисті <b>{name_playlist}</b>"


def delete(id_trak):
    with con.cursor() as curs:
        curs.execute(f"SELECT name_trak FROM trak WHERE id LIKE '{id_trak}'")
        name_trak = curs.fetchall()
        curs.execute(f"DELETE FROM trak WHERE id LIKE '{id_trak}'")
        con.commit()
        return [i['name_trak'] for i in name_trak][-1]


# print(delete_trak(428392590, 'dsd', 'Big Skeelz Что такое Днепр [mp3uk.net]'))

# try:
#     connection = pymysql.connect(
#         host=host,
#         user=user,
#         port=3306,
#         password=password,
#         database=db_name,
#         cursorclass=pymysql.cursors.DictCursor
#     )
#
#     try:
#
#         with connection.cursor() as cursor:

            # create_table = "CREATE TABLE user(" \
            #                "id INT PRIMARY KEY AUTO_INCREMENT, " \
            #                "name_genre VARCHAR(50));"
            # cursor.execute(create_table)

            # prob = "SELECT name_genre FROM user"
            # cursor.execute(prob)
            # print([int(i['name_genre']) for i in cursor.fetchall()])

        # mycurs = connection.cursor()

        # mycurs.execute('CREATE DATABASE playlist')

        # mycurs.execute('SHOW DATABASES')
        # for i in mycurs:
        #     print(i)

        # mycurs.execute('CREATE TABLE students (name VARCHAR(255), age INTEGER(10))')

        # mycurs.execute('SHOW TABLES')
        # for i in mycurs:
        #     print(i)

        # sql_form = "INSERT INTO students (name, age) VALUES(%s, %s)"
        # stud1 = ('Kevin', 22)
        # mycurs.execute(sql_form, stud1)
        # connection.commit()

        # sql_form = "INSERT INTO students (name, age) VALUES(%s, %s)"
        # stud1 = [('Bohda', 20),
        #          ('Roma', 23),
        #          ('Kolia', 28),
        #          ('Alex', 32),
        #          ('Vladimir', 42)]
        # mycurs.executemany(sql_form, stud1)
        # connection.commit()

        # mycurs.execute("SELECT * FROM students WHERE name LIKE 'Kolia'")
        # for i in mycurs.fetchall():     # fetchone()
        #     print(i)

        # mycurs.execute("UPDATE students SET age=20 WHERE age > 24")     # изменили данные в табл
        # connection.commit()
        # mycurs.execute("SELECT * FROM students  ")
        # for i in mycurs.fetchall():  # fetchone()
        #     print(i)

        # mycurs.execute("DELETE FROM students WHERE name = 'Roma'")
        # connection.commit()

        # mycurs.execute("DROP TABLE students")
        # mycurs.execute("DROP TABLE IF EXISTS students")   # мы удаляем табл если она существует чтобы не вызывать ошибки
        # connection.commit()

#         print('succses')
#     finally:
#         connection.close()
#
# except:
#     print('No')

# t = "CREATE TABLE trak(" \
#             "id INT PRIMARY KEY AUTO_INCREMENT, " \
#             "playlist_id INT, " \
#             "name_trak VARCHAR(200), " \
#             "id_trak VARCHAR(200)," \
#             "FOREIGN KEY (playlist_id) REFERENCES playlist (id) ON DELETE CASCADE);"

# try:
#     connection = pymysql.connect(
#         host=host,
#         user=user,
#         port=3306,
#         password=password,
#         database=db_name,
#         cursorclass=pymysql.cursors.DictCursor
#     )
#     with connection.cursor() as cursor:
#         t = "DELETE FROM playlist WHERE name_genre LIKE 'aza' AND user_id LIKE '1'"
#         cursor.execute(t)
#         connection.commit()
#
# except Exception as ex:
#     print('no')