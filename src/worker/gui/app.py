# TODO: PasswordManagerApp отвечает за создание графического интерфейса пользователя,обработку событий,
#  взаимодействие с пользователем через всплывающие окнаи отображение данных в таблице Treeview. Этот класс
#  использует методы класса DBManager для управления паролями.
import string
import tkinter as tk
import random
from tkinter import ttk, messagebox
from tkinter import PhotoImage

from database import dbManager


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Менеджер паролей")
        self.geometry("700x400")

        self.icon_image = PhotoImage(file="src/assets/app-icon.png")
        self.iconphoto(False, self.icon_image)

        self.create_widgets()
        self.password_visible = False

    def create_widgets(self):
        input_frame = ttk.Frame(self)
        input_frame.pack(pady=10)

        self.service_label = ttk.Label(input_frame, text="Сервис:")
        self.service_label.grid(row=0, column=0, padx=5)

        self.service_entry = ttk.Entry(input_frame)
        self.service_entry.grid(row=0, column=1, padx=5)

        self.login_label = ttk.Label(input_frame, text="Логин:")
        self.login_label.grid(row=0, column=2, padx=5)

        self.login_entry = ttk.Entry(input_frame)
        self.login_entry.grid(row=0, column=3, padx=5)

        self.password_label = ttk.Label(input_frame, text="Пароль:")
        self.password_label.grid(row=0, column=4, padx=5)

        self.password_entry = ttk.Entry(input_frame)
        self.password_entry.grid(row=0, column=5, padx=5)

        self.add_button = ttk.Button(input_frame, text="Создать пароль", command=self.add_password)
        self.add_button.grid(row=1, column=3, padx=5)

        self.tree = ttk.Treeview(self, columns=("Service", "Login", "Password"), show='headings')
        self.tree.heading("Service", text="Сервис")
        self.tree.heading("Login", text="Логин")
        self.tree.heading("Password", text="Пароль")
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Button-3>", self.on_right_click)

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        self.show_all_button = ttk.Button(button_frame, text="Показать все пароли", command=self.show_all_passwords)
        self.show_all_button.grid(row=0, column=0, padx=5)

        self.show_button = ttk.Button(button_frame, text="Показать пароль", command=self.show_password)
        self.show_button.grid(row=0, column=1, padx=5)

        self.delete_button = ttk.Button(button_frame, text="Удалить пароль", command=self.delete_password)
        self.delete_button.grid(row=0, column=2, padx=5)

        self.exit_button = ttk.Button(button_frame, text="Выход", command=self.close)
        self.exit_button.grid(row=0, column=3, padx=5)

    def on_double_click(self, event):
        selected_item = self.tree.selection()[0]
        service = self.tree.item(selected_item, "values")[0]
        self.service_entry.delete(0, tk.END)
        self.service_entry.insert(0, service)

    def on_right_click(self, event):
        popup_menu = tk.Menu(self.tree, tearoff=0)
        popup_menu.add_command(label="Удалить пароль", command=self.delete_password)
        popup_menu.post(event.x_root, event.y_root)

    def add_password(self):
        service = self.service_entry.get().strip()
        if not service:
            messagebox.showwarning("Ошибка", "Пожалуйста, введите логин")
            return

        login = self.login_entry.get().strip()
        if not login:
            messagebox.showwarning("Ошибка", "Пожалуйста, введите логин")
            return

        password = self.password_entry.get().strip()
        password = password if password else generate_password()

        dbManager.add_credentials(service, login, password)
        self.service_entry.delete(0, tk.END)
        messagebox.showinfo("Успех", "Пароль успешно создан.")

    def show_password(self):
        service = self.service_entry.get().strip()
        if service:
            if self.password_visible:
                self.tree.delete(*self.tree.get_children())
                self.show_button.config(text="Показать пароль")
                self.password_visible = False
            else:
                if self.show_all_button["text"] == "Скрыть все пароли":

                    for item in self.tree.get_children():
                        if self.tree.item(item)["values"][0] != service:
                            self.tree.delete(item)
                    self.show_all_button.config(
                        text="Показать все пароли")
                else:
                    credentials = dbManager.get_credentials(service)
                    if credentials:
                        for credential in credentials:
                            self.tree.insert("", "end", values=(service, credential["login"], credential["password"]))
                            self.show_button.config(text="Скрыть пароль")
                            self.password_visible = True
                    else:
                        messagebox.showerror("Ошибка",
                                             "Пароль не найден.")
        else:
            messagebox.showwarning("Выбор",
                                   "Пожалуйста, введите название сервиса.")

    def delete_password(self):
        service = self.service_entry.get().strip()
        login = self.login_entry.get().strip()
        if not service:
            messagebox.showwarning("Выбор", "Пожалуйста, введите название сервиса.")
            return
        if not login:
            messagebox.showwarning("Выбор", "Пожалуйста, введите логин")
            return

        dbManager.delete_credentials(service, login)
        messagebox.showinfo("Удаление", f"Пароль для {service} удален.")

    def show_all_passwords(self):
        if self.show_all_button["text"] == "Показать все пароли":
            for item in self.tree.get_children():
                self.tree.delete(item)

            credentials = dbManager.get_all_credentials()
            for row in credentials:
                self.tree.insert("", "end", values=(row[0], row[1], row[2]))

            self.show_all_button.config(text="Скрыть все пароли")
        else:
            for item in self.tree.get_children():
                self.tree.delete(item)

            self.show_all_button.config(text="Показать все пароли")

    def close(self):
        self.destroy()


def generate_password() -> str:
    """
    DEPRECATED
    """
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(32))
    return password
