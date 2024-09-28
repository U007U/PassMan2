import os
import string
import random
from tkinter import messagebox, ttk
import tkinter as tk
from PIL import ImageTk
import customtkinter as ctk
from database import dbManager


class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Менеджер паролей")
        self.geometry("650x400")
        self.iconpath = ImageTk.PhotoImage(file=os.path.join("assets", "app-icon.png"))
        self.wm_iconbitmap()
        self.iconphoto(False, self.iconpath)

        self.create_widgets()
        self.password_visible = False

    def create_widgets(self):
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(pady=10)

        self.service_label = ctk.CTkLabel(input_frame, text="Сервис:")
        self.service_label.grid(row=0, column=0, padx=5)

        self.service_entry = ctk.CTkEntry(input_frame)
        self.service_entry.grid(row=0, column=1, padx=5)

        self.login_label = ctk.CTkLabel(input_frame, text="Логин:")
        self.login_label.grid(row=0, column=2, padx=5)

        self.login_entry = ctk.CTkEntry(input_frame)
        self.login_entry.grid(row=0, column=3, padx=5)

        self.password_label = ctk.CTkLabel(input_frame, text="Пароль:")
        self.password_label.grid(row=0, column=4, padx=5)

        self.password_entry = ctk.CTkEntry(input_frame)
        self.password_entry.grid(row=0, column=5, padx=5)

        self.add_button = ctk.CTkButton(input_frame, text="Создать пароль", command=self.add_password)
        self.add_button.grid(row=1, column=3, padx=5)


        # Создаем прокручиваемый фрейм для Treeview
        self.tree_frame = ctk.CTkScrollableFrame(self)
        self.tree_frame.pack(pady=10, fill=ctk.BOTH,
                             expand=True)  # Упаковываем фрейм с отступами и позволяя ему расширяться

        # Создаем стиль для Treeview
        style = ttk.Style()
        style.configure("Treeview", background="#B7B7B7", foreground="#000000",
                        rowheight=25)  # Настраиваем фон, цвет текста и высоту строк
        style.configure("Treeview.Heading", background="#B7B7B7",
                        foreground="#0C5D9B")  # Настраиваем фон и цвет текста заголовков колонок

        # Создаем Treeview внутри прокручиваемого фрейма
        self.tree = ttk.Treeview(self.tree_frame, columns=("Service", "Login", "Password"), show='headings',
                                 style="Treeview")

        # Устанавливаем заголовки колонок
        self.tree.heading("Service", text="Сервис")  # Заголовок для колонки "Сервис"
        self.tree.heading("Login", text="Логин")  # Заголовок для колонки "Логин"
        self.tree.heading("Password", text="Пароль")  # Заголовок для колонки "Пароль"

        # Устанавливаем ширину колонок
        self.tree.column("Service", width=150)  # Ширина колонки "Сервис"
        self.tree.column("Login", width=150)  # Ширина колонки "Логин"
        self.tree.column("Password", width=250)  # Ширина колонки "Пароль"

        # Создаем прокрутку для Treeview
        tree_scrollbar = ctk.CTkScrollbar(self.tree_frame)
        tree_scrollbar.pack(side="right", fill="y")  # Упаковываем полосу прокрутки справа, заполняя по вертикали

        # Настраиваем прокрутку для Treeview
        self.tree.configure(yscrollcommand=tree_scrollbar.set)  # Связываем прокрутку с Treeview
        tree_scrollbar.configure(command=self.tree.yview)  # Связываем Treeview с прокруткой

        # Добавляем Treeview в окно
        self.tree.pack(fill=tk.BOTH, expand=True)  # Упаковываем Treeview, позволяя ему заполнять доступное пространство



        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=10)

        # All buttons with their commands
        self.show_all_button = ctk.CTkButton(button_frame, text="Показать все пароли", command=self.show_all_passwords)
        self.show_all_button.grid(row=0, column=0, padx=5)

        self.show_button = ctk.CTkButton(button_frame, text="Показать пароль", command=self.show_password)
        self.show_button.grid(row=0, column=1, padx=5)

        self.delete_button = ctk.CTkButton(button_frame, text="Удалить пароль", command=self.delete_password)
        self.delete_button.grid(row=0, column=2, padx=5)

        self.exit_button = ctk.CTkButton(button_frame, text="Выход", command=self.close)
        self.exit_button.grid(row=0, column=3, padx=5)

        # Bind double-click event to show service in entry field
        self.tree.bind("<Double-1>", self.on_double_click)

        # Bind right-click event to show popup menu
        self.tree.bind("<Button-3>", self.on_right_click)

    def on_double_click(self, event):
        selected_item = self.tree.selection()  # Get selected item
        if selected_item:  # Check if an item is selected
            service = self.tree.item(selected_item[0], "values")[0]  # Get service name from the selected item
            login = self.tree.item(selected_item[0], "values")[1]  # Get login from the selected item
            # Clear and set the service and login entries
            self.service_entry.delete(0, tk.END)
            self.service_entry.insert(0, service)
            self.login_entry.delete(0, tk.END)
            self.login_entry.insert(0, login)


    def on_right_click(self, event):
        selected_item = self.tree.selection()  # Get selected item
        if selected_item:  # Check if an item is selected
            popup_menu = tk.Menu(self.tree, tearoff=0)
            popup_menu.add_command(label="Удалить пароль", command=self.delete_password)
            popup_menu.post(event.x_root, event.y_root)

    def add_password(self):
        service = self.service_entry.get().strip()
        if not service:
            messagebox.showwarning("Ошибка", "Пожалуйста введите сервис")
            return

        login = self.login_entry.get().strip()
        if not login:
            messagebox.showwarning("Ошибка", "Пожалуйста введите логин")
            return

        password = self.password_entry.get().strip()
        if not password:
            password = generate_password()

        # Check if the credentials already exist
        existing_credentials = dbManager.get_credentials(service)
        if any(cred["login"] == login for cred in existing_credentials):
            messagebox.showwarning("Ошибка", "Пароль для этого сервиса и логина уже существует.")
            return

        dbManager.add_credentials(service, login, password)
        messagebox.showinfo("Успех", "Пароль успешно создан.")

        # Clear fields after adding
        self.service_entry.delete(0, tk.END)
        self.login_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)


    def show_password(self):
        # Получаем название сервиса из поля ввода
        service = self.service_entry.get().strip()

        if service:
            # Проверьте, виден ли пароль в данный момент
            if self.password_visible:
                # Скрыть пароль
                self.tree.delete(*self.tree.get_children())  # Очистить все элементы в древовидном представлении
                self.service_entry.delete(0, tk.END)  # Очистите сервисную запись
                self.login_entry.delete(0, tk.END)  # Очистите сервисную запись
                self.show_button.configure(text="Показать пароль")  # Изменить текст кнопки
                self.password_visible = False  # Обновить флаг видимости
            else:
                # Показать пароль
                credentials = dbManager.get_credentials(service)
                if credentials:
                    for credential in credentials:
                        values = (service, credential["login"], credential["password"])
                        self.tree.delete(*self.tree.get_children())  # Очистить все элементы в древовидном представлении
                        self.tree.insert("", "end", values=values)  # Вставить в древовидное представление
                    self.show_button.configure(text="Скрыть пароль")  # Изменить текст кнопки

                    self.show_all_button.configure(text="Показать все пароли")
                    setattr(self, 'password_visible', True)  # Обновляем флаг видимости

                else:
                    messagebox.showerror("Ошибка", "Пароль не найден.")
        else:
            messagebox.showwarning("Выбор", "Пожалуйста, введите название сервиса.")



    def delete_password(self):
        selected_item = self.tree.selection()  # Get selected item
        if selected_item:  # Check if an item is selected
            service = self.tree.item(selected_item[0], "values")[0]  # Get service name from the selected item
            login = self.tree.item(selected_item[0], "values")[1]  # Get login from the selected item

            dbManager.delete_credentials(service, login)  # Delete credentials from the database

            messagebox.showinfo("Удаление", f"Пароль для {service} удален.")

            # Clear the service and login entries after deletion.
            self.service_entry.delete(0, tk.END)
            self.login_entry.delete(0, tk.END)

            # Remove the selected item from the Treeview.
            for item in selected_item:
                self.tree.delete(item)
        else:
            messagebox.showwarning("Выбор", "Пожалуйста выберите пароль для удаления.")

    def show_all_passwords(self):
        if hasattr(self, 'show_all_button') and (self.show_all_button.cget("text") == "Показать все пароли"):
            for item in list(self.tree.get_children()):
                self.tree.delete(item)  # Clear existing items in the tree view

            credentials = dbManager.get_all_credentials()

            for row in credentials:
                # Hide the password by replacing it with asterisks
                hidden_password = "*" * len(row[2])
                self.tree.insert("", "end", values=(row[0], row[1], hidden_password))

            self.show_all_button.configure(text="Скрыть все пароли")
        else:
            for item in list(self.tree.get_children()):
                self.tree.delete(item)  # Clear existing items in the tree view

            self.show_all_button.configure(text="Показать все пароли")


    def close(self):
        """Close the application."""
        self.destroy()


def generate_password() -> str:
    """
    Generate a random password.
    """
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(32))
    return password



