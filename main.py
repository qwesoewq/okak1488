import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import random
import json
from dataclasses import dataclass, asdict, field
from typing import List, Optional

# Структура цитаты
@dataclass
class Quote:
    text: str
    author: str
    topic: str

# Пример предопределённых цитат
DEFAULT_QUOTES = [
    Quote("Жизнь — это то, что с тобой происходит, пока ты строишь планы.", "Джон Леннон", "Жизнь"),
    Quote("Учение — свет, а неучение — тьма.", "Аристотель", "Мудрость"),
    Quote("Если хочешь иметь то, что никогда не имел — делай то, что никогда не делал.", "Неизвестен", "Мотивация"),
    Quote("Не бойтесь совершенства — вам его не достичь.", "Сальвадор Дали", "Юмор"),
    Quote("Счастье — это реальность, воспринятая через ожидания.", "Неизвестен", "Философия")
]

class QuotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор цитат")
        self.root.geometry("800x500")

        # Данные
        self.quotes: List[Quote] = DEFAULT_QUOTES.copy()
        self.history: List[Quote] = []

        # Верхняя панель: генерация и добавление
        top_frame = ttk.Frame(root, padding=8)
        top_frame.pack(fill='x')

        self.generate_btn = ttk.Button(top_frame, text="Сгенерировать цитату", command=self.generate_quote)
        self.generate_btn.pack(side='left')

        self.add_btn = ttk.Button(top_frame, text="Добавить цитату", command=self.add_quote_dialog)
        self.add_btn.pack(side='left', padx=(8,0))

        self.save_btn = ttk.Button(top_frame, text="Сохранить историю (JSON)", command=self.save_history)
        self.save_btn.pack(side='right')

        self.load_btn = ttk.Button(top_frame, text="Загрузить историю (JSON)", command=self.load_history)
        self.load_btn.pack(side='right', padx=(0,8))

        # Центр: текущая цитата
        center_frame = ttk.Frame(root, padding=8)
        center_frame.pack(fill='x')

        self.quote_text = tk.Text(center_frame, height=4, wrap='word', state='disabled', bg='#f6f6f6')
        self.quote_text.pack(fill='x', padx=4, pady=4)

        # Фильтры
        filter_frame = ttk.LabelFrame(root, text="Фильтры", padding=8)
        filter_frame.pack(fill='x', padx=8, pady=6)

        ttk.Label(filter_frame, text="Автор:").pack(side='left', padx=(0,6))
        self.author_var = tk.StringVar()
        self.author_combo = ttk.Combobox(filter_frame, textvariable=self.author_var, state='readonly')
        self.author_combo.pack(side='left')
        self.author_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        ttk.Label(filter_frame, text="Тема:").pack(side='left', padx=(12,6))
        self.topic_var = tk.StringVar()
        self.topic_combo = ttk.Combobox(filter_frame, textvariable=self.topic_var, state='readonly')
        self.topic_combo.pack(side='left')
        self.topic_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        clear_btn = ttk.Button(filter_frame, text="Сбросить фильтры", command=self.clear_filters)
        clear_btn.pack(side='right')

        # Нижняя часть: история (список)
        bottom_frame = ttk.Frame(root, padding=8)
        bottom_frame.pack(fill='both', expand=True)

        self.history_list = tk.Listbox(bottom_frame)
        self.history_list.pack(side='left', fill='both', expand=True, padx=(0,4))
        self.history_list.bind('<Double-1>', self.show_history_quote)

        scrollbar = ttk.Scrollbar(bottom_frame, orient='vertical', command=self.history_list.yview)
        scrollbar.pack(side='left', fill='y')
        self.history_list.config(yscrollcommand=scrollbar.set)

        # Инициализация списков фильтров
        self.refresh_filter_options()

    def refresh_filter_options(self):
        authors = sorted({q.author for q in self.quotes})
        topics = sorted({q.topic for q in self.quotes})
        self.author_combo['values'] = ['<Все>'] + authors
        self.topic_combo['values'] = ['<Все>'] + topics
        self.author_combo.set('<Все>')
        self.topic_combo.set('<Все>')
        self.apply_filters()

    def apply_filters(self):
        author = self.author_var.get()
        topic = self.topic_var.get()
        filtered = self.history
        if author and author != '<Все>':
            filtered = [q for q in filtered if q.author == author]
        if topic and topic != '<Все>':
            filtered = [q for q in filtered if q.topic == topic]
        self.populate_history_list(filtered)

    def clear_filters(self):
        self.author_combo.set('<Все>')
        self.topic_combo.set('<Все>')
        self.populate_history_list(self.history)

    def populate_history_list(self, items: Optional[List[Quote]] = None):
        if items is None:
            items = self.history
        self.history_list.delete(0, tk.END)
        for i, q in enumerate(items, start=1):
            display = f"{i}. \"{q.text}\" — {q.author} [{q.topic}]"
            self.history_list.insert(tk.END, display)

    def generate_quote(self):
        # Если есть выбранные фильтры для источников (тут генерируем из self.quotes), можно расширить
        if not self.quotes:
            messagebox.showwarning("Нет цитат", "Список цитат пуст. Добавьте новые цитаты.")
            return
        q = random.choice(self.quotes)
        self.show_current_quote(q)
        self.history.append(q)
        self.refresh_filter_options()  # на случай, если добавлены новые авторы/темы
        self.apply_filters()

    def show_current_quote(self, q: Quote):
        self.quote_text.config(state='normal')
        self.quote_text.delete('1.0', tk.END)
        self.quote_text.insert(tk.END, f"\"{q.text}\"\n\n— {q.author}    [{q.topic}]")
        self.quote_text.config(state='disabled')

    def show_history_quote(self, event):
        sel = self.history_list.curselection()
        if not sel:
            return
        index = sel[0]
        # Фильтры могут изменить видимый список; возьмём отображаемую строку и найдем соответствующую цитату
        line = self.history_list.get(index)
        # Показать диалог с полным текстом
        messagebox.showinfo("Цитата из истории", line)

    def add_quote_dialog(self):
        text = simpledialog.askstring("Новая цитата", "Текст цитаты:")
        if text is None:
            return  # отмена
        text = text.strip()
        if not text:
            messagebox.showerror("Ошибка ввода", "Текст цитаты не может быть пустым.")
            return

        author = simpledialog.askstring("Новая цитата", "Автор:")
        if author is None:
            return
        author = author.strip()
        if not author:
            messagebox.showerror("Ошибка ввода", "Автор не может быть пустым.")
            return

        topic = simpledialog.askstring("Новая цитата", "Тема:")
        if topic is None:
            return
        topic = topic.strip()
        if not topic:
            messagebox.showerror("Ошибка ввода", "Тема не может быть пустой.")
            return

        new_q = Quote(text, author, topic)
        self.quotes.append(new_q)
        messagebox.showinfo("Добавлено", "Цитата успешно добавлена в список источников.")
        self.refresh_filter_options()

    def save_history(self):
        if not self.history:
            if not messagebox.askyesno("Пустая история", "История пуста. Всё равно сохранить файл?"):
                return
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files","*.json"),("All files","*.*")])
        if not path:
            return
        # Сохраняем историю (список цитат) в JSON
        data = [asdict(q) for q in self.history]
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Сохранено", f"История сохранена в {path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

    def load_history(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files","*.json"),("All files","*.*")])
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            loaded = []
            for item in data:
                # Простая валидация полей
                t = item.get('text') or item.get('quote') or ""
                a = item.get('author') or ""
                top = item.get('topic') or item.get('theme') or ""
                if not t.strip() or not a.strip() or not top.strip():
                    # Пропускаем некорректные записи
                    continue
                loaded.append(Quote(t.strip(), a.strip(), top.strip()))
            if not loaded:
                messagebox.showwarning("Ничего не загружено", "В файле нет корректных записей цитат.")
                return
            self.history = loaded
            self.populate_history_list()
            self.refresh_filter_options()
            messagebox.showinfo("Загружено", f"Загружено {len(loaded)} цитат(ы) в историю.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = QuotesApp(root)
    root.mainloop()