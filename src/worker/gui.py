# TODO: PasswordManagerApp отвечает за создание графического интерфейса пользователя,обработку событий,
#  взаимодействие с пользователем через всплывающие окнаи отображение данных в таблице Treeview. Этот класс
#  использует методы класса DBManager для управления паролями.
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import PhotoImage
from utils.dbManager import DBManager
from utils.passwordManager import generate_password
from cryptography.fernet import Fernet


#######################################################################################################################
class PasswordManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Менеджер паролей")
        self.geometry("700x400")

        # Установка значка окна
        self.icon_image = PhotoImage(file="../assets/app-icon.png")
        self.iconphoto(False, self.icon_image)

        self.db_manager = DBManager()
        self.key = self.db_manager.key
        self.fernet = Fernet(self.key)

        self.create_widgets()
        self.password_visible = False  # Переменная для отслеживания видимости пароля

    def create_widgets(self):
        input_frame = ttk.Frame(self)
        input_frame.pack(pady=10)

        self.service_label = ttk.Label(input_frame, text="Сервис:")
        self.service_label.grid(row=0, column=0, padx=5)

        self.service_entry = ttk.Entry(input_frame)
        self.service_entry.grid(row=0, column=1, padx=5)

        self.add_button = ttk.Button(input_frame, text="Создать пароль", command=self.add_password)
        self.add_button.grid(row=0, column=2, padx=5)

        # Фрейм для отображения паролей
        self.tree = ttk.Treeview(self, columns=("Service", "Password"), show='headings')
        self.tree.heading("Service", text="Сервис")
        self.tree.heading("Password", text="Пароль")
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        # Добавляем обработчики событий
        self.tree.bind("<Double-1>", self.on_double_click)  # Двойной клик
        self.tree.bind("<Button-3>", self.on_right_click)  # Правый клик

        # Кнопки управления
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        self.show_all_button = ttk.Button(button_frame, text="Показать все пароли", command=self.show_all_passwords)
        self.show_all_button.grid(row=0, column=0, padx=5)

        self.show_button = ttk.Button(button_frame, text="Показать пароль", command=self.show_password)
        self.show_button.grid(row=0, column=1, padx=5)

        self.delete_button = ttk.Button(button_frame, text="Удалить пароль", command=self.delete_password)
        self.delete_button.grid(row=0, column=2, padx=5)

        self.generate_button = ttk.Button(button_frame, text="Сгенерировать новый пароль",
                                          command=self.generate_new_password)
        self.generate_button.grid(row=0, column=3, padx=5)

        self.exit_button = ttk.Button(button_frame, text="Выход", command=self.close)
        self.exit_button.grid(row=0, column=4, padx=5)

    def on_double_click(self):
        selected_item = self.tree.selection()[0]  # Получаем выбранный элемент
        service = self.tree.item(selected_item, "values")[0]  # Получаем название сервиса
        self.service_entry.delete(0, tk.END)  # Очищаем поле ввода
        self.service_entry.insert(0, service)  # Заполняем его названием сервиса

    def on_right_click(self, event):
        popup_menu = tk.Menu(self.tree, tearoff=0)  # Создаем всплывающее меню
        popup_menu.add_command(label="Удалить пароль", command=self.delete_password)
        popup_menu.add_command(label="Сгенерировать новый пароль", command=self.generate_new_password)
        popup_menu.post(event.x_root, event.y_root)  # Показываем меню в месте клика

    ##################################################################################################################################

    def add_password(self):
        service = self.service_entry.get().strip()  # Получаем название сервиса из поля ввода и удаляем лишние пробелы
        password = generate_password()  # Генерируем новый пароль
        encrypted_password = self.fernet.encrypt(password.encode())  # Шифруем пароль

        # Сохраняем сервис и зашифрованный пароль в базе данных
        if self.db_manager.add_password(service, encrypted_password):
            self.service_entry.delete(0, tk.END)  # Очищаем поле ввода
            messagebox.showinfo("Успех", "Пароль успешно создан.")  # Показываем сообщение об успешном создании
        else:
            messagebox.showerror("Ошибка", "Не удалось сохранить пароль.")  # Сообщение об ошибке

    def generate_new_password(self):
        service = self.service_entry.get().strip()  # Получаем название сервиса из поля ввода
        if service:  # Проверяем, введено ли название сервиса
            new_password = generate_password()  # Генерируем новый пароль
            encrypted_password = self.fernet.encrypt(new_password.encode())  # Шифруем новый пароль

            # Обновляем пароль в базе данных
            if self.db_manager.add_password(service,
                                            encrypted_password):  # Используем метод add_password для обновления
                messagebox.showinfo("Успех",
                                    f"Новый пароль для {service} успешно сгенерирован.")  # Сообщаем об успешном обновлении
                self.service_entry.delete(0, tk.END)  # Очищаем поле ввода
            else:
                messagebox.showerror("Ошибка", "Не удалось обновить пароль.")  # Сообщение об ошибке
        else:
            messagebox.showwarning("Выбор",
                                   "Пожалуйста, введите название сервиса.")  # Предупреждение, если сервис не выбран

    ##################################################################

    def show_password(self):
        service = self.service_entry.get().strip()  # Получаем название сервиса из поля ввода
        if service:  # Проверяем, введено ли название сервиса
            if self.password_visible:  # Если пароль уже виден
                self.tree.delete(*self.tree.get_children())  # Удаляем все записи из таблицы
                self.show_button.config(text="Показать пароль")  # Меняем текст кнопки на "Показать пароль"
                self.password_visible = False  # Устанавливаем флаг, что пароль теперь скрыт
            else:  # Если пароль скрыт
                if self.show_all_button["text"] == "Скрыть все пароли":  # Если показаны все пароли
                    # Очищаем таблицу, оставляя только выбранный пароль
                    for item in self.tree.get_children():
                        if self.tree.item(item)["values"][0] != service:
                            self.tree.delete(item)
                    self.show_all_button.config(
                        text="Показать все пароли")  # Меняем текст кнопки на "Показать все пароли"
                else:  # Если показывается только выбранный пароль
                    password = self.db_manager.get_password(service)  # Получаем пароль для указанного сервиса
                    if password:  # Проверяем, найден ли пароль
                        self.tree.insert("", "end", values=(service, password))  # Добавляем запись в таблицу Treeview
                        self.show_button.config(text="Скрыть пароль")  # Меняем текст кнопки на "Скрыть пароль"
                        self.password_visible = True  # Устанавливаем флаг, что пароль теперь виден
                    else:
                        messagebox.showerror("Ошибка",
                                             "Пароль не найден.")  # Выводим сообщение об ошибке, если пароль не найден
        else:
            messagebox.showwarning("Выбор",
                                   "Пожалуйста, введите название сервиса.")  # Выводим предупреждение, если сервис не выбран

    ##########################################################################################################################

    def delete_password(self):
        service = self.service_entry.get().strip()  # Получаем название сервиса из поля ввода
        if service:  # Проверяем, введено ли название сервиса
            if self.db_manager.delete_password(service):  # Удаляем пароль из базы данных
                messagebox.showinfo("Удаление",
                                    f"Пароль для {service} удален.")  # Показываем сообщение об успешном удалении
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить пароль.")  # Сообщение об ошибке
        else:
            messagebox.showwarning("Выбор",
                                   "Пожалуйста, введите название сервиса.")  # Предупреждение, если сервис не выбран

    def show_all_passwords(self):
        if self.show_all_button["text"] == "Показать все пароли":  # Проверяем текущий текст кнопки
            # Очистка существующих записей в таблице
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Получение всех паролей из базы данных
            self.db_manager.c.execute("SELECT service, password FROM passwords")
            rows = self.db_manager.c.fetchall()

            # Заполнение таблицы данными
            for row in rows:
                service = row[0]
                encrypted_password = row[1]
                try:
                    # Декодируем пароль
                    password = self.db_manager.fernet.decrypt(encrypted_password).decode()
                    self.tree.insert("", "end", values=(service, password))
                except Exception as e:
                    print(f"Ошибка при расшифровке пароля для сервиса {service}: {e}")

            self.show_all_button.config(text="Скрыть все пароли")  # Меняем текст кнопки на "Скрыть все пароли"
        else:
            # Очистка таблицы, чтобы скрыть пароли
            for item in self.tree.get_children():
                self.tree.delete(item)

            self.show_all_button.config(text="Показать все пароли")  # Меняем текст кнопки на "Показать все пароли"

    def close(self):
        self.db_manager.close()  # Закрываем соединение с базой данных
        self.destroy()  # Уничтожаем главное окно приложения
