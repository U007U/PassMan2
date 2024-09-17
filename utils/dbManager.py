# TODO: DBManager отвечает за взаимодействие с базой данных: создание таблиц, генерацию ключа шифрования,
# шифрование и дешифрование паролей, добавление, получение и удаление паролей. Этот класс не имеет никакого
# отношения к графическому интерфейсу.
import sqlite3
from cryptography.fernet import Fernet


class DBManager:
    def __init__(self, db_name='passwords.db'):
        self.conn = sqlite3.connect(db_name)
        self.c = self.conn.cursor()
        self.create_metadata_table()  # Создаем таблицу для хранения ключа шифрования
        self.key = self.get_or_create_key()  # Получаем или создаем ключ шифрования
        self.fernet = Fernet(self.key)  # Инициализируем Fernet с ключом шифрования
        self.create_passwords_table()  # Создаем таблицу для хранения паролей

    def create_metadata_table(self):
        self.c.execute('''CREATE TABLE IF NOT EXISTS metadata (key BLOB)''')
        self.conn.commit()

    def create_passwords_table(self):
        self.c.execute('''CREATE TABLE IF NOT EXISTS passwords (service TEXT PRIMARY KEY, password BLOB)''')
        self.conn.commit()

    def get_or_create_key(self):
        self.c.execute("SELECT key FROM metadata LIMIT 1")
        key = self.c.fetchone()
        if key:
            return key[0]
        else:
            new_key = Fernet.generate_key()
            self.c.execute("INSERT INTO metadata (key) VALUES (?)", (new_key,))
            self.conn.commit()
            return new_key

    def add_password(self, service, encrypted_password):
        try:
            # Выполняем SQL-запрос для вставки или замены записи в таблице passwords
            # service - название сервиса, encrypted_password - зашифрованный пароль
            self.c.execute("INSERT OR REPLACE INTO passwords (service, password) VALUES (?, ?)",
                           (service, encrypted_password))

            # Сохраняем изменения в базе данных
            self.conn.commit()

            # Возвращаем True, если запись успешно добавлена
            return True
        except Exception as e:
            # Если произошла ошибка, выводим сообщение об ошибке в консоль
            print(f"Ошибка при добавлении пароля: {e}")

            # Возвращаем False в случае ошибки
            return False

    def get_password(self, service):
        self.c.execute("SELECT password FROM passwords WHERE service = ?", (service,))
        encrypted_password = self.c.fetchone()
        if encrypted_password:
            return self.fernet.decrypt(encrypted_password[0]).decode()  # Декодируем и возвращаем пароль
        return None  # Возвращаем None, если пароль не найден

    def delete_password(self, service):
        try:
            self.c.execute("DELETE FROM passwords WHERE service = ?", (service,))
            self.conn.commit()
            return True  # Возвращаем True, если пароль успешно удален
        except Exception as e:
            print(f"Ошибка при удалении пароля: {e}")
            return False  # Возвращаем False в случае ошибки

    def close(self):
        self.conn.close()
