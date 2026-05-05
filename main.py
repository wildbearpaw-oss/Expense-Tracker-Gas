import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox


class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("900x600")

        self.data_file = "expenses.json"
        self.expenses = []
        self.load_data()

        self.setup_ui()
        self.update_table()

    def setup_ui(self):
        # Фрейм ввода данных
        input_frame = ttk.LabelFrame(self.root, text="Добавить расходы", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Сумма
        ttk.Label(input_frame, text="Сумма: ").grid(row=0, column=0, sticky="w", padx=5)
        self.amount_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.amount_var, width=15).grid(row=0, column=1, padx=5)

        # Категория
        ttk.Label(input_frame, text="Категория: ").grid(row=0, column=2, sticky="w", padx=5)
        self.category_var = tk.StringVar(value="еда")
        categories = ["еда", "коммунальные платежи", "транспорт", "развлечения", "здоровье", "одежда", "другое"]
        ttk.Combobox(input_frame, textvariable=self.category_var, values=categories, width=15).grid(row=0, column=3,
                                                                                                    padx=5)

        # Дата
        ttk.Label(input_frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=4, sticky="w", padx=5)
        self.date_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.date_var, width=15).grid(row=0, column=5, padx=5)

        # Кнопка добавления
        ttk.Button(input_frame, text="Добавить расход", command=self.add_expense).grid(row=0, column=6, padx=10)

        # Фрейм фильтров
        filter_frame = ttk.LabelFrame(self.root, text="Фильтры", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        # Фильтр по категории
        ttk.Label(filter_frame, text="Категория:").grid(row=0, column=0, sticky="w", padx=5)
        self.filter_category_var = tk.StringVar(value="все")
        filter_categories = ["все"] + categories
        self.category_filter = ttk.Combobox(filter_frame, textvariable=self.filter_category_var,
                                            values=filter_categories, width=15)
        self.category_filter.grid(row=0, column=1, padx=5)
        self.category_filter.bind('<<ComboboxSelected>>', lambda e: self.update_table())

        # Фильтр по дате
        ttk.Label(filter_frame, text="С даты:").grid(row=0, column=2, sticky="w", padx=5)
        self.date_from_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.date_from_var, width=15).grid(row=0, column=3, padx=5)

        ttk.Label(filter_frame, text="По дату:").grid(row=0, column=4, sticky="w", padx=5)
        self.date_to_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.date_to_var, width=15).grid(row=0, column=5, padx=5)

        ttk.Button(filter_frame, text="Применить", command=self.update_table).grid(row=0, column=6, padx=10)
        ttk.Button(filter_frame, text="Сбросить", command=self.reset_filters).grid(row=0, column=7, padx=5)

        # Таблица расходов
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("Сумма", "Категория", "Дата")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Итоговая сумма
        self.total_label = ttk.Label(self.root, text="Общая сумма: 0.00 руб.", font=("Arial", 12, "bold"))
        self.total_label.pack(pady=10)

    def validate_input(self):
        # Проверка суммы
        try:
            amount = float(self.amount_var.get())
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом")
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную сумму (число)")
            return False

        # Проверка даты
        try:
            datetime.strptime(self.date_var.get(), "%d.%m.%Y")
        except ValueError:
            messagebox.showerror("Ошибка", "Дата должна быть в формате ДД.ММ.ГГГГ")
            return False

        return True

    def add_expense(self):
        if not self.validate_input():
            return

        expense = {
            "amount": float(self.amount_var.get()),
            "category": self.category_var.get(),
            "date": self.date_var.get()
        }

        self.expenses.append(expense)
        self.save_data()
        self.update_table()

        # Очистка полей
        self.amount_var.set("")
        self.date_var.set("")

    def update_table(self):
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)

        filtered_expenses = self.get_filtered_expenses()
        total = 0

        for expense in filtered_expenses:
            self.tree.insert("", "end", values=(
                f"{expense['amount']:.2f}",
                expense['category'],
                expense['date']
            ))
            total += expense['amount']

        self.total_label.config(text=f"Общая сумма: {total:.2f} руб.")

    def get_filtered_expenses(self):
        filtered = self.expenses

        # Фильтр по категории
        category = self.filter_category_var.get()
        if category != "все":
            filtered = [e for e in filtered if e['category'] == category]

        # Фильтр по дате
        date_from = self.date_from_var.get()
        date_to = self.date_to_var.get()

        if date_from:
            try:
                from_date = datetime.strptime(date_from, "%d.%m.%Y")
                filtered = [e for e in filtered
                            if datetime.strptime(e['date'], "%d.%m.%Y") >= from_date]
            except ValueError:
                pass

        if date_to:
            try:
                to_date = datetime.strptime(date_to, "%d.%m.%Y")
                filtered = [e for e in filtered
                            if datetime.strptime(e['date'], "%d.%m.%Y") <= to_date]
            except ValueError:
                pass

        return filtered

    def reset_filters(self):
        self.filter_category_var.set("все")
        self.date_from_var.set("")
        self.date_to_var.set("")
        self.update_table()

    def save_data(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.expenses, f, ensure_ascii=False, indent=2)

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.expenses = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.expenses = []


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
