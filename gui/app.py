from datetime import date
import tkinter as tk
from tkinter import ttk, messagebox
import models.library_models as lm
from services.library import Library


class App:
    def __init__(self):
        self.library = Library()
        self.root = tk.Tk()
        self.root.title("Library Management System")
        self.root.geometry("900x560")

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True)

        self.dashboard_tab = ttk.Frame(self.tabs)
        self.books_tab = ttk.Frame(self.tabs)
        self.users_tab = ttk.Frame(self.tabs)
        self.borrow_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.dashboard_tab, text="Dashboard")
        self.tabs.add(self.books_tab, text="Books")
        self.tabs.add(self.users_tab, text="Users")
        self.tabs.add(self.borrow_tab, text="Borrow / Return")
        self.build_dashboard()
        self.refresh_dashboard()
        self.build_books_tab()
        self.refresh_books()
        self.build_users_tab()
        self.refresh_users()
        self.build_borrow_tab()
        self.refresh_borrow_tab()
        self.tabs.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)


    def build_dashboard(self):
        self.stat_labels = {}
        names = [
            ("total_books", "Total Books"),
            ("available_books", "Available Books"),
            ("total_users", "Total Users"),
            ("active_borrowings", "Active Borrowings"),
            ("overdue_borrowings", "Overdue Borrowings"),
        ]
        for key, text in names:
            frame = ttk.LabelFrame(self.dashboard_tab, text=text)
            frame.pack(side="left", padx=10, pady=20, ipadx=10, ipady=10)
            label = ttk.Label(frame, text="0", font=("Arial", 24))
            label.pack()
            self.stat_labels[key] = label

    def refresh_dashboard(self):
        stats = self.library.get_stats()
        for key in self.stat_labels:
            self.stat_labels[key].config(text=str(stats[key])) 

    def build_books_tab(self):
        top = ttk.Frame(self.books_tab)
        top.pack(fill="x", padx=10, pady=10)

        ttk.Label(top, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.search_var, width=25).pack(side="left", padx=5)
        ttk.Button(top, text="Search", command=self.refresh_books).pack(side="left")

        ttk.Label(top, text="Filter:").pack(side="left", padx=(20, 5))
        self.filter_var = tk.StringVar(value="All")
        filter_box = ttk.Combobox(top, textvariable=self.filter_var,
                                  values=["All", "Available", "Unavailable"],
                                  state="readonly", width=12)
        filter_box.pack(side="left")
        filter_box.bind("<<ComboboxSelected>>", self.on_filter_change)

        columns = ("id", "title", "author", "category", "copies")
        self.books_table = ttk.Treeview(self.books_tab, columns=columns, show="headings", height=10)
        headings = {"id": "ID", "title": "Title", "author": "Author",
                    "category": "Category", "copies": "Available / Total"}
        for col in columns:
            self.books_table.heading(col, text=headings[col])
            self.books_table.column(col, width=140)
        self.books_table.pack(fill="both", expand=True, padx=10)

        form = ttk.Frame(self.books_tab)
        form.pack(fill="x", padx=10, pady=10)
        self.book_vars = {}
        fields = [("id", "Book ID"), ("title", "Title"), ("author", "Author"),
                  ("category", "Category"), ("copies", "Copies")]
        column = 0
        for key, text in fields:
            ttk.Label(form, text=text).grid(row=0, column=column, padx=5)
            var = tk.StringVar()
            ttk.Entry(form, textvariable=var, width=16).grid(row=1, column=column, padx=5)
            self.book_vars[key] = var
            column += 1

        buttons = ttk.Frame(self.books_tab)
        buttons.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Button(buttons, text="Add", command=self.add_book).pack(side="left", padx=5)
        ttk.Button(buttons, text="Update", command=self.update_book).pack(side="left", padx=5)
        ttk.Button(buttons, text="Delete", command=self.delete_book).pack(side="left", padx=5)

    def refresh_books(self):
        text = self.search_var.get()
        if text.strip() != "":
            books = self.library.search_books(text)
        else:
            books = self.library.get_all_books()
        choice = self.filter_var.get()

        for item in self.books_table.get_children():
            self.books_table.delete(item)

        for book in books:
            if choice == "Available" and not book.is_available():
                continue
            if choice == "Unavailable" and book.is_available():
                continue
            copies = str(book.available_copies) + " / " + str(book.total_copies)
            self.books_table.insert("", "end", iid=book.id,
                                    values=(book.id, book.title, book.author.name,
                                            book.category.name, copies))

    def on_filter_change(self, event):
        self.refresh_books()

    def read_book_form(self):
        book_id = self.book_vars["id"].get().strip()
        title = self.book_vars["title"].get().strip()
        author_name = self.book_vars["author"].get().strip()
        category_name = self.book_vars["category"].get().strip()
        copies = self.book_vars["copies"].get().strip()
        if book_id == "" or title == "" or author_name == "" or category_name == "":
            raise ValueError("Book ID, title, author and category are required")
        author = lm.Author("A-" + book_id, author_name, "Unknown")
        category = lm.Category("C-" + category_name, category_name)
        return book_id, title, author, category, copies

    def add_book(self):
        try:
            book_id, title, author, category, copies = self.read_book_form()
            if not copies.isdigit():
                raise ValueError("Copies must be a number")
            book = lm.Book(book_id, title, author, category, int(copies))
            self.library.add_book(book)
            messagebox.showinfo("Done", "Book added successfully")
            for key in self.book_vars:
                self.book_vars[key].set("")
            self.refresh_dashboard()
            self.refresh_books()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def update_book(self):
        try:
            book_id, title, author, category, copies = self.read_book_form()
            self.library.update_book(book_id, title, author, category)
            messagebox.showinfo("Done", "Book updated successfully")
            self.refresh_books()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def delete_book(self):
        book_id = self.book_vars["id"].get().strip()
        if book_id == "":
            messagebox.showerror("Error", "Enter the Book ID first")
            return
        if not messagebox.askyesno("Confirm", "Delete book " + book_id + "?"):
            return
        try:
            self.library.delete_book(book_id)
            messagebox.showinfo("Done", "Book deleted")
            for key in self.book_vars:
                self.book_vars[key].set("")
            self.refresh_dashboard()
            self.refresh_books()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def build_users_tab(self):
        columns = ("id", "name", "email", "type", "limit")
        self.users_table = ttk.Treeview(self.users_tab, columns=columns, show="headings", height=10)
        headings = {"id": "ID", "name": "Name", "email": "Email",
                    "type": "Type", "limit": "Max Books"}
        for col in columns:
            self.users_table.heading(col, text=headings[col])
            self.users_table.column(col, width=150)
        self.users_table.pack(fill="both", expand=True, padx=10, pady=10)

        form = ttk.Frame(self.users_tab)
        form.pack(fill="x", padx=10, pady=10)
        self.user_vars = {}
        fields = [("id", "User ID"), ("name", "Name"), ("email", "Email")]
        column = 0
        for key, text in fields:
            ttk.Label(form, text=text).grid(row=0, column=column, padx=5)
            var = tk.StringVar()
            ttk.Entry(form, textvariable=var, width=20).grid(row=1, column=column, padx=5)
            self.user_vars[key] = var
            column += 1

        ttk.Label(form, text="Type").grid(row=0, column=column, padx=5)
        self.user_type_var = tk.StringVar(value="Student")
        ttk.Combobox(form, textvariable=self.user_type_var, values=["Student", "Teacher"],
                     state="readonly", width=12).grid(row=1, column=column, padx=5)

        ttk.Button(self.users_tab, text="Add User", command=self.add_user).pack(padx=10, pady=(0, 10), anchor="w")

    def refresh_users(self):
        for item in self.users_table.get_children():
            self.users_table.delete(item)
        for user in self.library.get_all_users():
            if isinstance(user, lm.Student):
                user_type = "Student"
            else:
                user_type = "Teacher"
            self.users_table.insert("", "end", iid=user.id,
                                    values=(user.id, user.name, user.email,
                                            user_type, user.max_books_allowed()))

    def add_user(self):
        try:
            user_id = self.user_vars["id"].get().strip()
            name = self.user_vars["name"].get().strip()
            email = self.user_vars["email"].get().strip()
            if user_id == "":
                raise ValueError("User ID is required")
            if self.user_type_var.get() == "Student":
                user = lm.Student(user_id, name, email)
            else:
                user = lm.Teacher(user_id, name, email)
            self.library.add_user(user)
            messagebox.showinfo("Done", "User added successfully")
            for key in self.user_vars:
                self.user_vars[key].set("")
            self.refresh_users()
        except ValueError as e:
            messagebox.showerror("Error", str(e)) 

    def build_borrow_tab(self):
        top = ttk.Frame(self.borrow_tab)
        top.pack(fill="x", padx=10, pady=10)

        ttk.Label(top, text="User:").pack(side="left")
        self.user_choice = tk.StringVar()
        self.user_box = ttk.Combobox(top, textvariable=self.user_choice, width=25, state="readonly")
        self.user_box.pack(side="left", padx=5)

        ttk.Label(top, text="Book:").pack(side="left", padx=(15, 0))
        self.book_choice = tk.StringVar()
        self.book_box = ttk.Combobox(top, textvariable=self.book_choice, width=35, state="readonly")
        self.book_box.pack(side="left", padx=5)

        ttk.Button(top, text="Borrow", command=self.borrow).pack(side="left", padx=5)
        ttk.Button(top, text="Return", command=self.return_book).pack(side="left", padx=5)

        filter_row = ttk.Frame(self.borrow_tab)
        filter_row.pack(fill="x", padx=10)
        ttk.Label(filter_row, text="Show:").pack(side="left")
        self.borrow_filter_var = tk.StringVar(value="Active")
        borrow_filter = ttk.Combobox(filter_row, textvariable=self.borrow_filter_var,
                                     values=["Active", "Overdue", "Returned", "All"],
                                     state="readonly", width=12)
        borrow_filter.pack(side="left", padx=5)
        borrow_filter.bind("<<ComboboxSelected>>", self.on_borrow_filter_change)

        columns = ("id", "user", "book", "borrowed", "due", "returned", "status")
        self.borrow_table = ttk.Treeview(self.borrow_tab, columns=columns, show="headings", height=12)
        headings = {"id": "ID", "user": "User", "book": "Book", "borrowed": "Borrowed",
                    "due": "Due", "returned": "Returned", "status": "Status"}
        for col in columns:
            self.borrow_table.heading(col, text=headings[col])
            self.borrow_table.column(col, width=110)
        self.borrow_table.pack(fill="both", expand=True, padx=10, pady=10)

    def refresh_borrow_tab(self):
        users = []
        for user in self.library.get_all_users():
            users.append(user.id + " - " + user.name)
        books = []
        for book in self.library.get_all_books():
            books.append(book.id + " - " + book.title)
        self.user_box["values"] = users
        self.book_box["values"] = books

        for item in self.borrow_table.get_children():
            self.borrow_table.delete(item)
        choice = self.borrow_filter_var.get()
        today = date.today()
        for b in self.library.get_all_borrowings():
            if b.is_overdue(today):
                status = "Overdue"
            elif b.is_active():
                status = "Active"
            else:
                status = "Returned"
            if choice == "Active" and not b.is_active():
                continue
            if choice == "Overdue" and status != "Overdue":
                continue
            if choice == "Returned" and status != "Returned":
                continue
            returned = "-"
            if b.return_date is not None:
                returned = b.return_date.strftime("%Y-%m-%d")
            self.borrow_table.insert("", "end", iid=b.id,
                                     values=(b.id, b.user.name, b.book.title,
                                             b.borrow_date.strftime("%Y-%m-%d"),
                                             b.due_date().strftime("%Y-%m-%d"),
                                             returned, status))

    def on_borrow_filter_change(self, event):
        self.refresh_borrow_tab()

    def read_borrow_choice(self):
        user_text = self.user_choice.get()
        book_text = self.book_choice.get()
        if user_text == "" or book_text == "":
            raise ValueError("Select a user and a book first")
        return user_text.split(" - ")[0], book_text.split(" - ")[0]

    def refresh_all(self):
        self.refresh_dashboard()
        self.refresh_books()
        self.refresh_users()
        self.refresh_borrow_tab()

    def borrow(self):
        try:
            user_id, book_id = self.read_borrow_choice()
            self.library.borrow_book(user_id, book_id)
            messagebox.showinfo("Done", "Book borrowed successfully")
            self.refresh_all()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def return_book(self):
        try:
            user_id, book_id = self.read_borrow_choice()
            self.library.return_book(user_id, book_id)
            messagebox.showinfo("Done", "Book returned successfully")
            self.refresh_all()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def on_tab_changed(self, event):
        self.refresh_all()

    def on_close(self):
        self.library.save_all()
        self.root.destroy()

    def run(self):
        self.root.mainloop()