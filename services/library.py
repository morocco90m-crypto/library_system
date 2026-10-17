from datetime import date, datetime
import models.library_models as lm
from file_manager.file_manager import FileManager


class Library:
    def __init__(self, folder="data"):
        self.__file_manager = FileManager(folder)
        self.__books = {}
        self.__users = {}
        self.__borrowings = []
        self.load_all()

    def add_book(self, book):
        if not isinstance(book, lm.Book):
            raise ValueError("Invalid book")
        if book.id in self.__books:
            raise ValueError("Book ID already exists")
        self.__books[book.id] = book
        self.save_all()

    def get_book(self, book_id):
        if book_id not in self.__books:
            raise ValueError("Book not found")
        return self.__books[book_id]

    def get_all_books(self):
        return list(self.__books.values())

    def update_book(self, book_id, title=None, author=None, category=None):
        book = self.get_book(book_id)
        if title is not None:
            book.title = title
        if author is not None:
            book.author = author
        if category is not None:
            book.category = category
        self.save_all()

    def delete_book(self, book_id):
        self.get_book(book_id)
        for b in self.__borrowings:
            if b.book.id == book_id and b.is_active():
                raise ValueError("Book is currently borrowed and cannot be deleted")
        remaining = []
        for b in self.__borrowings:
            if b.book.id != book_id:
                remaining.append(b)
        self.__borrowings = remaining
        del self.__books[book_id]
        self.save_all()

    def add_user(self, user):
        if not isinstance(user, lm.User):
            raise ValueError("Invalid user")
        if user.id in self.__users:
            raise ValueError("User ID already exists")
        self.__users[user.id] = user
        self.save_all()

    def get_user(self, user_id):
        if user_id not in self.__users:
            raise ValueError("User not found")
        return self.__users[user_id]

    def get_all_users(self):
        return list(self.__users.values())

    def search_books(self, text):
        text = text.strip().lower()
        result = []
        for book in self.__books.values():
            if text in book.title.lower() or text in book.author.name.lower():
                result.append(book)
        return result

    def filter_books(self, available):
        result = []
        for book in self.__books.values():
            if book.is_available() == available:
                result.append(book)
        return result

    def borrow_book(self, user_id, book_id):
        user = self.get_user(user_id)
        book = self.get_book(book_id)                      # rule 4: book must exist
        already = False
        count = 0
        for b in self.__borrowings:
            if b.user.id == user_id and b.is_active():
                count += 1
                if b.book.id == book_id:
                    already = True
        if already:                                        # rule 2
            raise ValueError("User already borrowed this book")
        if not book.is_available():                        # rule 1
            raise ValueError("No copies available to borrow.")
        if count >= user.max_books_allowed():              # rule 3
            raise ValueError("Borrow limit reached")
        book.borrow_book()
        borrowing = lm.Borrowing(self._next_id(), user, book, date.today())
        self.__borrowings.append(borrowing)
        self.save_all()
        return borrowing

    def return_book(self, user_id, book_id):
        self.get_user(user_id)
        self.get_book(book_id)
        for b in self.__borrowings:
            if b.user.id == user_id and b.book.id == book_id and b.is_active():
                b.mark_returned(date.today())              # this also returns the copy to the book
                self.save_all()
                return b
        raise ValueError("No active borrowing found for this user and book")

    def _next_id(self):
        return "BR" + str(len(self.__borrowings) + 1)


    def get_all_borrowings(self):
        return list(self.__borrowings)

    def get_active_borrowings(self):
        result = []
        for b in self.__borrowings:
            if b.is_active():
                result.append(b)
        return result

    def get_overdue_borrowings(self):
        result = []
        for b in self.__borrowings:
            if b.is_overdue(date.today()):
                result.append(b)
        return result

    def get_borrowers(self, book_id):
        result = []
        for b in self.__borrowings:
            if b.book.id == book_id and b.is_active():
                result.append(b.user)
        return result

    def get_stats(self):
        return {
            "total_books": len(self.__books),
            "available_books": len(self.filter_books(True)),
            "total_users": len(self.__users),
            "active_borrowings": len(self.get_active_borrowings()),
            "overdue_borrowings": len(self.get_overdue_borrowings())
        }

    def save_all(self):
        books = []
        for book in self.__books.values():
            books.append(book.to_dict())
        users = []
        for user in self.__users.values():
            users.append(user.to_dict())
        borrowings = []
        for b in self.__borrowings:
            borrowings.append(b.to_dict())
        self.__file_manager.save("books.json", books)
        self.__file_manager.save("users.json", users)
        self.__file_manager.save("borrowings.json", borrowings)

    def load_all(self):
        for d in self.__file_manager.load("books.json"):
            author = lm.Author(d["author"]["id"], d["author"]["name"], d["author"]["country"])
            category = lm.Category(d["category"]["id"], d["category"]["name"])
            book = lm.Book(d["id"], d["title"], author, category, d["total_copies"])
            book.available_copies = d["available_copies"]
            self.__books[book.id] = book
        for d in self.__file_manager.load("users.json"):
            if d["user_type"] == "Student":
                user = lm.Student(d["id"], d["name"], d["email"])
            else:
                user = lm.Teacher(d["id"], d["name"], d["email"])
            self.__users[user.id] = user
        for d in self.__file_manager.load("borrowings.json"):
            user = self.__users.get(d["user_id"])
            book = self.__books.get(d["book_id"])
            if user is None or book is None:
                continue
            borrow_date = datetime.strptime(d["borrow_date"], "%Y-%m-%d").date()
            return_date = None
            if d["return_date"] is not None:
                return_date = datetime.strptime(d["return_date"], "%Y-%m-%d").date()
            self.__borrowings.append(lm.Borrowing(d["id"], user, book, borrow_date, return_date))