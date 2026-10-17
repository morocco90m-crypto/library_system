# Library Management System

## Team Members
- Mamdouh Mohammed Sabri (individual project)

## Project Description
A small desktop application that manages a library. The librarian can manage
books and users, lend books to students and teachers, take them back, and see
a dashboard with live numbers. The project was built with Python and
Object-Oriented Programming. Data is saved in JSON files and the interface is
made with Tkinter.

## Main Features
- Add, update and delete books
- Add users (Student or Teacher)
- Search books by title or author
- Filter books: All / Available / Unavailable
- Borrow and return books
- Track available copies of every book
- Track borrowers (who has which book, due dates, overdue)
- Borrowings list with filter: Active / Overdue / Returned / All
- Dashboard with real numbers: total books, available books, total users,
  active borrowings, overdue borrowings
- Data is loaded when the program starts and saved when it closes

## Classes
| Class | Role |
|---|---|
| `Entity` | Abstract base class for all entities (has the `id`) |
| `User` | Abstract class for library users (name, email) |
| `Student` | A user: max 5 books, 14 days |
| `Teacher` | A user: max 10 books, 30 days |
| `Author` | Book author (name, country) |
| `Category` | Book category (name) |
| `Book` | A book with total and available copies |
| `Borrowing` | One borrowing record (user, book, dates) |
| `Library` | Main class: books, users, borrowings and all the rules |
| `FileManager` | Reads and writes the JSON files |
| `App` | The Tkinter window (GUI) |

## OOP Concepts Used
| Concept | Where |
|---|---|
| Classes and objects | All classes above |
| Constructors | `__init__` in every class, children call `super().__init__()` |
| Encapsulation | Private attributes (`self.__name`) with properties and setters that validate |
| Properties | `name`, `email`, `title`, `available_copies`, `due_date`... |
| Inheritance | `Entity` -> `User` -> `Student` / `Teacher`; `Author`, `Category`, `Book`, `Borrowing` inherit `Entity` |
| Polymorphism | `Student` and `Teacher` implement `max_books_allowed()` and `borrowing_period()` differently; `Library` and `Borrowing` use them without checking the type |
| Abstraction | `Entity(ABC)` and `User` with `@abstractmethod` |
| Composition | `Book` has an `Author` and a `Category`; `Borrowing` has a `User` and a `Book`; `Library` has books, users and borrowings |
| Exception handling | `ValueError` is raised by the models and `Library`, and caught in the GUI with `try / except` |
| File handling | `FileManager` with `json` |

## Business Rules
1. A book cannot be borrowed if no copies are available.
2. A user cannot borrow the same book twice.
3. A user cannot exceed the maximum borrowing limit (Student 5, Teacher 10).
4. A book (and a user) must exist before borrowing.
5. A book that is currently borrowed cannot be deleted.
6. A borrowing can be returned only once.
7. Validation: name and title cannot be empty, email must contain `@`,
   number of copies must be a non-negative number, IDs must be unique.

## File Storage
No database is used. Data is saved as JSON files in the `data/` folder:
- `books.json`
- `users.json`
- `borrowings.json`

`FileManager` reads and writes them. `Library` loads them when it starts and
saves after every change and when the window is closed.

## GUI Framework
Tkinter (with `ttk` widgets): tabs for Dashboard, Books, Users and
Borrow / Return, with tables, forms, search and filter controls, and message
boxes for success and error messages.

## How to Run
1. Python 3 is required (Tkinter comes with it).
2. Open a terminal in the project folder.
3. (Optional) add sample data, only once:
   ```
   python seed_data.py
   ```
4. Start the application:
   ```
   python main.py
   ```

## Project Structure
```
library_system/
├── main.py
├── seed_data.py
├── models/
│   ├── entity.py
│   └── library_models.py
├── services/
│   └── library.py
├── file_manager/
│   └── file_manager.py
├── gui/
│   └── app.py
├── data/
│   ├── books.json
│   ├── users.json
│   └── borrowings.json
├── tests/
│   └── test_scenarios.txt
├── screenshots/
└── README.md
```

## Test Scenarios
11 scenarios (3 successful, 3 invalid input, 3 business-rule violations,
2 edge cases). The full list with steps and expected results is in
`tests/test_scenarios.txt`.

## Screenshots
| Screen | File |
|---|---|
| Dashboard | `screenshots/dashboard.png` |
| Books tab (table, search, filter) | `screenshots/books.png` |
| Users tab | `screenshots/users.png` |
| Borrow / Return tab | `screenshots/borrow.png` |
| Error message (business rule) | `screenshots/error.png` |
