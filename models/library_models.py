from abc import abstractmethod
from datetime import timedelta
import models.entity as entity


class User(entity.Entity):
    def __init__(self, user_id, name, email):
        super().__init__(user_id)
        self.name = name
        self.email = email

    @property
    def name(self):
        return self.__name
    
    @name.setter
    def name(self,value):
        if not value:
            raise ValueError("Name cannot be empty")
        self.__name = value

    @property
    def email(self):
        return self.__email
    
    @email.setter
    def email(self, value):
        if not value or "@" not in value:
            raise ValueError("Invalid email address")
        self.__email = value

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email
        }

    @abstractmethod
    def max_books_allowed(self):
        pass

    @abstractmethod
    def borrowing_period(self):
        pass



class Student(User):
    def max_books_allowed(self):
        return 5

    def borrowing_period(self):
        return 14 

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "user_type": "Student",
            "max_books_allowed": self.max_books_allowed(),
            "borrowing_period": self.borrowing_period()
        })
        return data


class Teacher(User):
    def max_books_allowed(self):
        return 10

    def borrowing_period(self):
        return 30  # days

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "user_type": "Teacher",
            "max_books_allowed": self.max_books_allowed(),
            "borrowing_period": self.borrowing_period()
        })
        return data


class Author(entity.Entity):
    def __init__(self, author_id, name, country):
        super().__init__(author_id)
        self.name = name
        self.__country = country

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        if not value:
            raise ValueError("Name cannot be empty")
        self.__name = value

    @property
    def country(self):
        return self.__country

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "country": self.country
        }


class Category(entity.Entity):
    def __init__(self, category_id, name):
        super().__init__(category_id)
        self.name = name

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        if not value:
            raise ValueError("Name cannot be empty")
        self.__name = value

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }

class Book(entity.Entity):
    def __init__(self, book_id, title, author, category,total_copies):
        super().__init__(book_id)
        self.title = title
        self.author = author
        self.category = category
        self.total_copies = total_copies
        self.available_copies = total_copies 

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, value):
        if not value:
            raise ValueError("Title cannot be empty")
        self.__title = value

    @property
    def author(self):
            return self.__author

    @author.setter
    def author(self, value):
        if not isinstance(value, Author):
            raise ValueError("Author must be an instance of Author class")
        self.__author = value

    @property
    def category(self):
            return self.__category

    @category.setter
    def category(self, value):
        if not isinstance(value, Category):
            raise ValueError("Category must be an instance of Category class")
        self.__category = value

    @property
    def total_copies(self):
        return self.__total_copies
    @total_copies.setter
    def total_copies(self, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError("Total copies must be a non-negative integer")
        self.__total_copies = value

    @property
    def available_copies(self):
        return self.__available_copies  

    @available_copies.setter
    def available_copies(self, value):
        if not isinstance(value, int) or value < 0 or value > self.total_copies:
            raise ValueError("Available copies must be a non-negative integer and cannot exceed total copies")
        self.__available_copies = value


    def is_available(self):
        return self.available_copies > 0

    def borrow_book(self):
        if not self.is_available():
            raise ValueError("No copies available to borrow.")
        self.available_copies = self.available_copies - 1

    def return_book(self):
        if self.available_copies < self.total_copies:
            self.available_copies += 1
            return True
        else:
            raise ValueError("All copies are already available.")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author.to_dict(),
            "category": self.category.to_dict(),
            "total_copies": self.total_copies,
            "available_copies": self.available_copies
            }
        

class Borrowing(entity.Entity):
    def __init__(self, borrowing_id, user, book, borrow_date, return_date=None):
        super().__init__(borrowing_id)
        self.user = user
        self.book = book
        self.borrow_date = borrow_date
        self.return_date = return_date

    @property
    def user(self):
        return self.__user

    @user.setter
    def user(self, value):
        if not isinstance(value, User):
            raise ValueError("User must be an instance of User class")
        self.__user = value

    @property
    def book(self):
        return self.__book

    @book.setter
    def book(self, value):
        if not isinstance(value, Book):
            raise ValueError("Book must be an instance of Book class")
        self.__book = value

    @property
    def borrow_date(self):
        return self.__borrow_date

    @borrow_date.setter
    def borrow_date(self, value):
        self.__borrow_date = value

    @property
    def return_date(self):
        return self.__return_date

    @return_date.setter
    def return_date(self, value):
        self.__return_date = value

    def due_date(self):
        return self.borrow_date + timedelta(days=self.user.borrowing_period())

    def is_active(self):
        return self.return_date is None

    def is_overdue(self, current_date):
        if self.is_active() and current_date > self.due_date():
            return True
        return False
    
    def mark_returned(self, return_date):
        if not self.is_active():
            raise ValueError("This borrowing record is already marked as returned.")
        self.book.return_book()
        self.return_date = return_date

    def to_dict(self):
        return_date = None
        if self.return_date is not None:
            return_date = self.return_date.strftime("%Y-%m-%d")
        return {
            "id": self.id,
            "user_id": self.user.id,
            "book_id": self.book.id,
            "borrow_date": self.borrow_date.strftime("%Y-%m-%d"),
            "due_date": self.due_date().strftime("%Y-%m-%d"),
            "return_date": return_date
        }