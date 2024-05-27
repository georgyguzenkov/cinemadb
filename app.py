import sys
import os
import psycopg2
import requests 
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.enums import TA_CENTER
import io
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, \
    QMessageBox, QTableWidget, QTableWidgetItem, QComboBox, QInputDialog, QDialog, QSpacerItem, QSizePolicy, QRadioButton, QButtonGroup
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QEvent, pyqtSignal

from psycopg2 import sql


class RegistrationWindow(QWidget):
    def __init__(self, db_connection):
        super().__init__()

        self.db_connection = db_connection
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Регистрация')
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        self.username_label = QLabel('Пользователь:')
        self.username_entry = QLineEdit()

        self.password_label = QLabel('Пароль:')
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password)

        self.role_label = QLabel('Права:')
        self.role_combobox = QComboBox()
        self.role_combobox.addItems(['Пользователь', 'Редактор'])

        register_button = QPushButton('Зарегистрировать')
        register_button.clicked.connect(self.register)

        layout.addWidget(self.username_label)
        layout.addWidget(self.username_entry)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_entry)
        layout.addWidget(self.role_label)
        layout.addWidget(self.role_combobox)
        layout.addWidget(register_button)

        self.setLayout(layout)

    def register(self):
        username = self.username_entry.text()
        password = self.password_entry.text()
        role = self.role_combobox.currentText().lower()

        cursor = self.db_connection.cursor()

        # Используем параметризованный запрос для безопасности
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            QMessageBox.warning(self, 'Регистрация', 'Пользователь с таким именем уже зарегистрирован.')
        else:
            # Используем параметризованный запрос для безопасности
            cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s) RETURNING user_id', (username, password))
            user_id = cursor.fetchone()[0]

            # Используем параметризованный запрос для безопасности
            cursor.execute('INSERT INTO user_roles (user_id, role) VALUES (%s, %s)', (user_id, role))

            self.db_connection.commit()
            QMessageBox.information(self, 'Регистрация', 'Пользователь зарегистрирован!')
            self.close()


class LoginWindow(QWidget):
    def __init__(self, db_connection, registration_window, view_movies_window, add_movie_window, view_promotions_window, view_users_window, view_sessions_window, view_tickets_window, view_viewers_window):
        super().__init__()

        self.db_connection = db_connection
        self.registration_window = registration_window
        self.view_movies_window = view_movies_window
        self.add_movie_window = add_movie_window
        self.view_promotions_window = view_promotions_window
        self.view_users_window = view_users_window
        self.view_sessions_window = view_sessions_window
        self.view_tickets_window = view_tickets_window
        self.view_viewers_window = view_viewers_window
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Кинотеатр')
        self.setGeometry(100, 100, 500, 200)

        main_layout = QVBoxLayout()

        self.logo_label = QLabel()
        pixmap = QPixmap('logoc.png')
        self.logo_label.setPixmap(pixmap)
        main_layout.addWidget(self.logo_label)

        form_layout = QVBoxLayout()

        self.username_label = QLabel('Пользователь:')
        self.username_entry = QLineEdit()

        self.password_label = QLabel('Пароль:')
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password)

        form_layout.addWidget(self.username_label)
        form_layout.addWidget(self.username_entry)
        form_layout.addWidget(self.password_label)
        form_layout.addWidget(self.password_entry)

        main_layout.addLayout(form_layout)

        button_layout = QHBoxLayout()

        login_button = QPushButton('Вход')
        login_button.setIcon(QIcon('icons/login.png'))
        login_button.clicked.connect(self.login)
        button_layout.addWidget(login_button)

        register_button = QPushButton('Регистрация')
        register_button.setIcon(QIcon('icons/register.png'))
        register_button.clicked.connect(self.show_registration)
        button_layout.addWidget(register_button)

        view_movies_button = QPushButton('Посмотреть фильмы')
        view_movies_button.setIcon(QIcon('icons/movies.png'))
        view_movies_button.clicked.connect(self.show_view_movies)
        button_layout.addWidget(view_movies_button)

        add_movie_button = QPushButton('Добавить фильм')
        add_movie_button.setIcon(QIcon('icons/add.png'))
        add_movie_button.clicked.connect(self.show_add_movie)
        button_layout.addWidget(add_movie_button)

        view_sessions_button = QPushButton('Сеансы')
        view_sessions_button.setIcon(QIcon('icons/sessions.png'))
        view_sessions_button.clicked.connect(self.show_view_sessions)
        button_layout.addWidget(view_sessions_button)

        view_tickets_button = QPushButton('Билеты')
        view_tickets_button.setIcon(QIcon('icons/tickets.png'))
        view_tickets_button.clicked.connect(self.show_view_tickets)
        button_layout.addWidget(view_tickets_button)

        view_viewers_button = QPushButton('Зрители')
        view_viewers_button.setIcon(QIcon('icons/viewers.png'))
        view_viewers_button.clicked.connect(self.show_view_viewers)
        button_layout.addWidget(view_viewers_button)

        view_users_button = QPushButton('Пользователи')
        view_users_button.setIcon(QIcon('icons/users.png'))
        view_users_button.clicked.connect(self.show_view_users)
        button_layout.addWidget(view_users_button)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def show_view_sessions(self):
        self.view_sessions_window.populate_table()
        self.view_sessions_window.show()

    def show_view_users(self):
        self.view_users_window.populate_table()
        self.view_users_window.show()

    def show_view_tickets(self):
        self.view_tickets_window.populate_table()
        self.view_tickets_window.show()

    def show_view_viewers(self):
        self.view_viewers_window.populate_table()
        self.view_viewers_window.show()

    def login(self):
        username = self.username_entry.text()
        password = self.password_entry.text()

        cursor = self.db_connection.cursor()

        # Используем параметризованный запрос для безопасности
        cursor.execute('''
            SELECT u.user_id, u.username, r.role
            FROM users u
            LEFT JOIN user_roles r ON u.user_id = r.user_id
            WHERE u.username = %s AND u.password = %s
        ''', (username, password))
        user_data = cursor.fetchone()

        if user_data:
            user_id, _, user_role = user_data
            self.determine_user_type(user_role, user_id)
            QMessageBox.information(self, 'Вход', 'Удачный вход!')
        else:
            QMessageBox.warning(self, 'Вход', 'Неправильный логин или пароль')

    def determine_user_type(self, user_role, user_id):
        if user_role == 'moderator':
            self.add_movie_window = AddMovieWindow(self.db_connection, user_id)
            self.add_movie_window.show()
        elif user_role == 'regular':
            self.view_movies_window.populate_table()
            self.view_movies_window.show()

    def show_registration(self):
        self.registration_window.show()

    def show_view_movies(self):
        self.view_movies_window.populate_table()
        self.view_movies_window.show()

    def show_add_movie(self):
        QMessageBox.warning(self, 'Добавить фильм', 'Только редакторы могут добавлять фильмы.')

    def show_view_promotions(self):
        self.view_promotions_window.populate_table()
        self.view_promotions_window.show()


class ViewMoviesWindow(QWidget):
    def __init__(self, db_connection):
        super().__init__()

        self.db_connection = db_connection
        self.sort_order = Qt.AscendingOrder  # Начальная сортировка по возрастанию
        self.column_sort_states = {}  # Словарь для отслеживания состояний сортировки каждого столбца
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Посмотреть фильмы')
        self.setGeometry(100, 100, 1700, 600)

        layout = QVBoxLayout()

        self.table_label = QLabel('Фильмы:')
        self.table_widget = QTableWidget(self)
        self.table_widget.setSortingEnabled(True)  # Включаем возможность сортировки

        # Добавление кнопок
        self.search_button = QPushButton('Поиск', self)
        self.clear_search_button = QPushButton('Очистить поиск', self)
        self.delete_row_button = QPushButton('Удалить строку', self)
        self.view_poster_button = QPushButton('Просмотр Постера', self)
        self.to_pdf_button = QPushButton('В PDF', self)
        self.edit_button = QPushButton('Режим редактора', self)

        self.search_button.setIcon(QIcon('icons/search.png'))
        self.clear_search_button.setIcon(QIcon('icons/clear.png'))
        self.delete_row_button.setIcon(QIcon('icons/delete.png'))
        self.view_poster_button.setIcon(QIcon('icons/view.png'))
        self.to_pdf_button.setIcon(QIcon('icons/pdf.png'))
        self.edit_button.setIcon(QIcon('icons/edit.png'))

        # Кнопки управления
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.search_button)
        buttons_layout.addWidget(self.clear_search_button)
        buttons_layout.addWidget(self.delete_row_button)
        buttons_layout.addWidget(self.view_poster_button)
        buttons_layout.addWidget(self.to_pdf_button)
        buttons_layout.addWidget(self.edit_button)

        layout.addWidget(self.table_label)
        layout.addWidget(self.table_widget)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)
        self.search_button.clicked.connect(self.search_in_table)
        self.clear_search_button.clicked.connect(self.clear_search)
        self.delete_row_button.clicked.connect(self.delete_selected_row)
        self.view_poster_button.clicked.connect(self.view_poster)
        self.to_pdf_button.clicked.connect(self.generate_pdf)
        self.edit_button.clicked.connect(self.enable_editing_mode)

        # Подключаем сигнал клика по заголовку к слоту сортировки
        self.table_widget.horizontalHeader().sectionClicked.connect(self.sort_by_column)

        self.populate_table()

    def populate_table(self):
        cursor = self.db_connection.cursor()

        # Используем параметризованный запрос для безопасности
        cursor.execute('SELECT * FROM movies ORDER BY movie_id ASC')
        movies = cursor.fetchall()

        self.table_widget.setRowCount(len(movies))
        self.table_widget.setColumnCount(11)
        self.table_widget.setColumnWidth(0, 80)  # Установка ширины столбца 'Фильм ID'
        self.table_widget.setColumnWidth(1, 200)  # Установка ширины столбца 'Название'
        self.table_widget.setColumnWidth(2, 100)  # Установка ширины столбца 'Дата Выхода'
        self.table_widget.setColumnWidth(3, 150)  # Установка ширины столбца 'Жанр'
        self.table_widget.setColumnWidth(4, 100)  # Установка ширины столбца 'Продолжительность'
        self.table_widget.setColumnWidth(5, 250)  # Установка ширины столбца 'Описание'
        self.table_widget.setColumnWidth(6, 250)  # Установка ширины столбца 'Постер'
        self.table_widget.setColumnWidth(7, 200)  # Установка ширины столбца 'Актёры'
        self.table_widget.setColumnWidth(8, 100)  # Установка ширины столбца 'Зал'
        self.table_widget.setColumnWidth(9, 100)  # Установка ширины столбца 'Цена'
        self.table_widget.setColumnWidth(10, 100)  # Установка ширины столбца 'Время'
        self.table_widget.setHorizontalHeaderLabels(['Фильм ID', 'Название', 'Дата Выхода', 'Жанр', 'Продолжительность', 'Описание', 'Постер', 'Актёры', 'Зал', 'Цена', 'Время'])

        for row, movie in enumerate(movies):
            for col, data in enumerate(movie):
                item = QTableWidgetItem(str(data))
                self.table_widget.setItem(row, col, item)

    def sort_by_column(self, column_index):
        # Проверяем текущее состояние сортировки для этого столбца и переключаем его
        if column_index in self.column_sort_states and self.column_sort_states[column_index] == Qt.AscendingOrder:
            self.column_sort_states[column_index] = Qt.DescendingOrder
        else:
            self.column_sort_states[column_index] = Qt.AscendingOrder

        # Сортируем таблицу по выбранному столбцу и направлению
        self.table_widget.sortItems(column_index, self.column_sort_states[column_index])

    def search_in_table(self):
        search_text = QInputDialog.getText(self, 'Поиск фильма', 'Введите текст для поиска:')
        if search_text[1]:  # Проверка, что пользователь нажал OK и строка не пуста
            for row in range(self.table_widget.rowCount()):
                match = False
                for col in range(self.table_widget.columnCount()):
                    item = self.table_widget.item(row, col)
                    if search_text[0].lower() in item.text().lower():
                        match = True
                        break
                self.table_widget.setRowHidden(row, not match)

    def clear_search(self):
        # Показать все строки, если они были скрыты
        for row in range(self.table_widget.rowCount()):
            self.table_widget.setRowHidden(row, False)

    def delete_selected_row(self):
        current_row = self.table_widget.currentRow()
        if current_row > -1:
            confirmation = QMessageBox.question(self, 'Удалить строку', 'Вы уверены, что хотите удалить выбранную строку?',
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if confirmation == QMessageBox.Yes:
                self.table_widget.removeRow(current_row)

    def view_poster(self):
        current_row = self.table_widget.currentRow()
        if current_row > -1:
            poster_item = self.table_widget.item(current_row, 6)  # Assuming 'Постер' column index is 6
            if poster_item:
                poster_url = poster_item.text()
                self.show_poster_window(poster_url)

    def show_poster_window(self, url):
        dialog = QDialog(self)
        dialog.setWindowTitle("Просмотр Постера")
        layout = QVBoxLayout()
        label = QLabel(dialog)
        try:
            response = requests.get(url)
            response.raise_for_status()
            pixmap = QPixmap()
            pixmap.loadFromData(response.content)
            label.setPixmap(pixmap)
        except requests.RequestException as e:
            label.setText("Не удалось загрузить изображение.")
        layout.addWidget(label)
        dialog.setLayout(layout)
        dialog.exec_()

    def generate_pdf(self):
        current_row = self.table_widget.currentRow()
        if current_row > -1:
            movie_data = []
            for col in range(self.table_widget.columnCount()):
                item = self.table_widget.item(current_row, col)
                movie_data.append(item.text())

            poster_url = movie_data[6]  # URL постера

            # Создание PDF
            pdf_file = "movie_card.pdf"
            doc = SimpleDocTemplate(pdf_file, pagesize=letter)
            story = []

            # Регистрация шрифта
            pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
            pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSansBold.ttf'))

            styles = getSampleStyleSheet()
            styles['Normal'].fontName = 'DejaVuSans'
            styles['Heading1'].fontName = 'DejaVuSans-Bold'

            # Заголовок
            story.append(Paragraph("Карточка фильма", styles['Heading1']))
            story.append(Spacer(1, 12))

            # Информация о фильме
            info_text = [
                f"Фильм ID: {movie_data[0]}",
                f"Название: {movie_data[1]}",
                f"Дата Выхода: {movie_data[2]}",
                f"Жанр: {movie_data[3]}",
                f"Продолжительность: {movie_data[4]}",
                f"Описание: {movie_data[5]}",
                f"Актёры: {movie_data[7]}",
                f"Зал: {movie_data[8]}",
                f"Цена: {movie_data[9]}",
                f"Время: {movie_data[10]}"
            ]

            for line in info_text:
                story.append(Paragraph(line, styles['Normal']))
                story.append(Spacer(1, 12))

            # Загрузка и добавление постера
            try:
                response = requests.get(poster_url)
                response.raise_for_status()
                image_stream = io.BytesIO(response.content)
                image = Image(image_stream, width=150, height=200)
                story.append(image)
            except requests.RequestException:
                story.append(Paragraph("Не удалось загрузить изображение.", styles['Normal']))

            doc.build(story)

            # Открытие PDF файла
            self.open_pdf(pdf_file)

    def open_pdf(self, file_path):
        dialog = QDialog(self)
        dialog.setWindowTitle("Просмотр PDF")
        layout = QVBoxLayout()
        label = QLabel(dialog)
        label.setText(f"PDF файл создан: {file_path}")
        layout.addWidget(label)
        dialog.setLayout(layout)
        dialog.finished.connect(lambda: self.open_pdf_in_os(file_path))
        dialog.exec_()

    def open_pdf_in_os(self, file_path):
        try:
            if os.name == 'posix':
                os.system(f'open "{file_path}"')
            elif os.name == 'nt':
                os.startfile(file_path)
            else:
                QMessageBox.information(self, "Ошибка", "Не поддерживаемая операционная система.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть PDF файл: {str(e)}")

    def enable_editing_mode(self):
        self.table_widget.setEditTriggers(QTableWidget.AllEditTriggers)
        QMessageBox.information(self, "Режим редактирования", "Теперь вы можете редактировать таблицу. Все изменения будут сохранены при выходе из программы.")
        self.installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() == QEvent.Close:
            self.save_changes_to_database()
        return super(ViewMoviesWindow, self).eventFilter(source, event)

    def save_changes_to_database(self):
        cursor = self.db_connection.cursor()
        for row in range(self.table_widget.rowCount()):
            movie_data = []
            for col in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, col)
                movie_data.append(item.text())
            cursor.execute("""
                UPDATE movies SET 
                title = %s, release_date = %s, genre = %s, duration_minutes = %s, description = %s, 
                poster_url = %s, actors = %s, hall_id = %s, ticket_price = %s, session_time = %s
                WHERE movie_id = %s
            """, (movie_data[1], movie_data[2], movie_data[3], movie_data[4], movie_data[5],
                movie_data[6], movie_data[7], movie_data[8], movie_data[9], movie_data[10], movie_data[0]))
        self.db_connection.commit()
        QMessageBox.information(self, "Сохранение данных", "Изменения успешно сохранены в базе данных.")



class AddMovieWindow(QWidget):
    def __init__(self, db_connection, user_id):
        super().__init__()

        self.db_connection = db_connection
        self.user_id = user_id
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Добавить фильм')
        self.setGeometry(100, 100, 300, 400)

        layout = QVBoxLayout()

        self.title_label = QLabel('Название:')
        self.title_entry = QLineEdit()

        self.release_date_label = QLabel('Дата выхода (в формате ГГГГ-ММ-ДД):')
        self.release_date_entry = QLineEdit()

        self.genre_label = QLabel('Жанр:')
        self.genre_entry = QLineEdit()

        self.duration_label = QLabel('Продолжительность (в минутах):')
        self.duration_entry = QLineEdit()

        self.description_label = QLabel('Описание:')
        self.description_entry = QLineEdit()

        self.poster_url_label = QLabel('Постер (ссылка):')
        self.poster_url_entry = QLineEdit()

        self.actors_label = QLabel('Актеры:')
        self.actors_entry = QLineEdit()

        self.hall_label = QLabel('Зал:')
        self.hall_combobox = QComboBox()
        self.load_halls()

        self.session_time_label = QLabel('Время сеанса (в формате ГГГГ-ММ-ДД ЧЧ:ММ):')
        self.session_time_entry = QLineEdit()

        self.ticket_price_label = QLabel('Цена билета:')
        self.ticket_price_entry = QLineEdit()

        add_button = QPushButton('Добавить фильм')
        add_button.clicked.connect(self.add_movie)

        layout.addWidget(self.title_label)
        layout.addWidget(self.title_entry)
        layout.addWidget(self.release_date_label)
        layout.addWidget(self.release_date_entry)
        layout.addWidget(self.genre_label)
        layout.addWidget(self.genre_entry)
        layout.addWidget(self.duration_label)
        layout.addWidget(self.duration_entry)
        layout.addWidget(self.description_label)
        layout.addWidget(self.description_entry)
        layout.addWidget(self.poster_url_label)
        layout.addWidget(self.poster_url_entry)
        layout.addWidget(self.actors_label)
        layout.addWidget(self.actors_entry)
        layout.addWidget(self.hall_label)
        layout.addWidget(self.hall_combobox)
        layout.addWidget(self.session_time_label)
        layout.addWidget(self.session_time_entry)
        layout.addWidget(self.ticket_price_label)
        layout.addWidget(self.ticket_price_entry)
        layout.addWidget(add_button)

        self.setLayout(layout)

    def load_halls(self):
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT hall_id, hall_name FROM halls')
        halls = cursor.fetchall()
        for hall in halls:
            self.hall_combobox.addItem(hall[1], hall[0])

    def add_movie(self):
        title = self.title_entry.text()
        release_date = self.release_date_entry.text()
        genre = self.genre_entry.text()
        duration = self.duration_entry.text()
        description = self.description_entry.text()
        poster_url = self.poster_url_entry.text()
        actors = self.actors_entry.text()
        hall_id = self.hall_combobox.currentData()
        session_time = self.session_time_entry.text()
        ticket_price = self.ticket_price_entry.text()

        cursor = self.db_connection.cursor()

        cursor.execute('INSERT INTO movies (title, release_date, genre, duration_minutes, description, poster_url, actors, hall_id, ticket_price, session_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING movie_id',
                       (title, release_date, genre, duration, description, poster_url, actors, hall_id, ticket_price, session_time))
        movie_id = cursor.fetchone()[0]

        cursor.execute('INSERT INTO sessions (movie_id, hall_id, session_time, ticket_price) VALUES (%s, %s, %s, %s)',
                       (movie_id, hall_id, session_time, ticket_price))
        self.db_connection.commit()
        QMessageBox.information(self, 'Добавить фильм', 'Фильм успешно добавлен!')
        self.close()

class CreateSessionWindow(QWidget):
    session_added = pyqtSignal()  # Создаем сигнал

    def __init__(self, db_connection):
        super().__init__()

        self.db_connection = db_connection
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Создать сеанс')
        self.setGeometry(100, 100, 300, 400)

        layout = QVBoxLayout()

        self.movie_label = QLabel('Фильм:')
        self.movie_combobox = QComboBox()
        self.load_movies()

        self.hall_label = QLabel('Зал:')
        self.hall_combobox = QComboBox()
        self.load_halls()

        self.session_time_label = QLabel('Время начала (в формате ГГГГ-ММ-ДД ЧЧ:ММ):')
        self.session_time_entry = QLineEdit()

        self.end_time_label = QLabel('Время окончания (в формате ГГГГ-ММ-ДД ЧЧ:ММ):')
        self.end_time_entry = QLineEdit()

        add_button = QPushButton('Добавить сеанс')
        add_button.clicked.connect(self.add_session)

        layout.addWidget(self.movie_label)
        layout.addWidget(self.movie_combobox)
        layout.addWidget(self.hall_label)
        layout.addWidget(self.hall_combobox)
        layout.addWidget(self.session_time_label)
        layout.addWidget(self.session_time_entry)
        layout.addWidget(self.end_time_label)
        layout.addWidget(self.end_time_entry)
        layout.addWidget(add_button)

        self.setLayout(layout)

    def load_movies(self):
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT movie_id, title FROM movies')
        movies = cursor.fetchall()
        for movie in movies:
            self.movie_combobox.addItem(movie[1], movie[0])

    def load_halls(self):
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT hall_id, hall_name FROM halls')
        halls = cursor.fetchall()
        for hall in halls:
            self.hall_combobox.addItem(hall[1], hall[0])

    def add_session(self):
        movie_id = self.movie_combobox.currentData()
        hall_id = self.hall_combobox.currentData()
        session_time = self.session_time_entry.text()
        end_time = self.end_time_entry.text()

        cursor = self.db_connection.cursor()
        cursor.execute('INSERT INTO sessions (movie_id, hall_id, session_time, end_time) VALUES (%s, %s, %s, %s)',
                       (movie_id, hall_id, session_time, end_time))
        self.db_connection.commit()
        QMessageBox.information(self, 'Создать сеанс', 'Сеанс успешно создан!')
        self.session_added.emit()  # Испускаем сигнал
        self.close()


class ViewSessionsWindow(QWidget):
    def __init__(self, db_connection):
        super().__init__()

        self.db_connection = db_connection
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Посмотреть сеансы')
        self.setWindowIcon(QIcon('icons/sessions.png'))
        self.setGeometry(100, 100, 1000, 400)

        layout = QVBoxLayout()

        self.table_label = QLabel('Сеансы:')
        self.table_widget = QTableWidget(self)

        # Добавляем выпадающий список для выбора зала
        self.hall_combobox = QComboBox()
        self.hall_combobox.addItem('Все Залы', None)
        self.load_halls()

        # Добавляем выпадающий список для выбора времени суток
        self.time_combobox = QComboBox()
        self.time_combobox.addItem('Все Время', None)
        self.time_combobox.addItem('Утренние (до 12:00)', 'morning')
        self.time_combobox.addItem('Дневные (12:00 - 18:00)', 'afternoon')
        self.time_combobox.addItem('Вечерние (после 18:00)', 'evening')

        create_session_button = QPushButton('Создать сеанс')
        create_session_button.setIcon(QIcon('icons/add.png'))
        create_session_button.clicked.connect(self.show_create_session)

        delete_session_button = QPushButton('Удалить сеанс')
        delete_session_button.setIcon(QIcon('icons/delete.png'))
        delete_session_button.clicked.connect(self.delete_selected_session)

        # Добавляем элементы в layout
        layout.addWidget(self.table_label)
        layout.addWidget(self.hall_combobox)  # Добавляем выпадающий список зала в layout
        layout.addWidget(self.time_combobox)  # Добавляем выпадающий список времени суток в layout
        layout.addWidget(self.table_widget)
        layout.addWidget(create_session_button)
        layout.addWidget(delete_session_button)

        self.setLayout(layout)

        self.hall_combobox.currentIndexChanged.connect(self.populate_table)  # Обновляем таблицу при изменении выбора зала
        self.time_combobox.currentIndexChanged.connect(self.populate_table)  # Обновляем таблицу при изменении выбора времени суток

        self.populate_table()

    def load_halls(self):
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT hall_id, hall_name FROM halls')
        halls = cursor.fetchall()
        for hall in halls:
            self.hall_combobox.addItem(hall[1], hall[0])

    def populate_table(self):
        cursor = self.db_connection.cursor()
        hall_id = self.hall_combobox.currentData()
        time_filter = self.time_combobox.currentData()

        query = '''
            SELECT s.session_id, s.movie_id, m.title, s.hall_id, s.session_time, s.ticket_price, s.end_time
            FROM sessions s
            JOIN movies m ON s.movie_id = m.movie_id
        '''
        params = []
        
        if hall_id is not None or time_filter is not None:
            query += ' WHERE '
            conditions = []
            if hall_id is not None:
                conditions.append('s.hall_id = %s')
                params.append(hall_id)
            if time_filter is not None:
                if time_filter == 'morning':
                    conditions.append("s.session_time::time < '12:00'")
                elif time_filter == 'afternoon':
                    conditions.append("s.session_time::time BETWEEN '12:00' AND '18:00'")
                elif time_filter == 'evening':
                    conditions.append("s.session_time::time > '18:00'")
            query += ' AND '.join(conditions)
        
        cursor.execute(query, tuple(params))
        sessions = cursor.fetchall()

        self.table_widget.setRowCount(len(sessions))
        self.table_widget.setColumnCount(7)
        self.table_widget.setHorizontalHeaderLabels(['ID Сеанса', 'ID Фильма', 'Название Фильма', 'Зал', 'Время начала', 'Цена', 'Время окончания'])

        for row, session in enumerate(sessions):
            for col, data in enumerate(session):
                item = QTableWidgetItem(str(data))
                self.table_widget.setItem(row, col, item)

    def show_create_session(self):
        self.create_session_window = CreateSessionWindow(self.db_connection)
        self.create_session_window.session_added.connect(self.populate_table)  # Подключаем сигнал к методу
        self.create_session_window.show()

    def delete_selected_session(self):
        current_row = self.table_widget.currentRow()
        if current_row > -1:
            session_id_item = self.table_widget.item(current_row, 0)
            if session_id_item:
                session_id = session_id_item.text()
                confirmation = QMessageBox.question(self, 'Удалить сеанс', 'Вы уверены, что хотите удалить выбранный сеанс?',
                                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if confirmation == QMessageBox.Yes:
                    cursor = self.db_connection.cursor()
                    cursor.execute('DELETE FROM sessions WHERE session_id = %s', (session_id,))
                    self.db_connection.commit()
                    self.table_widget.removeRow(current_row)
                    QMessageBox.information(self, 'Удалить сеанс', 'Сеанс успешно удален!')





class ViewUsersWindow(QWidget):
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Просмотр пользователей')
        self.setGeometry(100, 100, 600, 300)
        layout = QVBoxLayout()
        self.table_widget = QTableWidget(self)
        layout.addWidget(self.table_widget)
        self.setLayout(layout)

    def populate_table(self):
        cursor = self.db_connection.cursor()
        cursor.execute('''
            SELECT u.username, r.role
            FROM users u
            JOIN user_roles r ON u.user_id = r.user_id
        ''')
        users = cursor.fetchall()
        self.table_widget.setRowCount(len(users))
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(['Имя пользователя', 'Права'])
        for row, user in enumerate(users):
            self.table_widget.setItem(row, 0, QTableWidgetItem(user[0]))
            self.table_widget.setItem(row, 1, QTableWidgetItem(user[1]))


class ViewPromotionsWindow(QWidget):
    def __init__(self, db_connection):
        super().__init__()

        self.db_connection = db_connection
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Посмотреть промоакции')
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        self.table_label = QLabel('Таблица промо:')
        self.table_widget = QTableWidget(self)

        layout.addWidget(self.table_label)
        layout.addWidget(self.table_widget)

        self.setLayout(layout)

    def populate_table(self):
        cursor = self.db_connection.cursor()

        # Используем параметризованный запрос для безопасности
        cursor.execute('SELECT * FROM promotions')
        promotions = cursor.fetchall()

        self.table_widget.setRowCount(len(promotions))
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(['ID Промо', 'Имя', 'Процент скидки', 'Дата начала', 'Дата окончания'])

        for row, promotion in enumerate(promotions):
            for col, data in enumerate(promotion):
                item = QTableWidgetItem(str(data))
                self.table_widget.setItem(row, col, item)


class AddTicketWindow(QWidget):
    def __init__(self, db_connection, parent):
        super().__init__()

        self.db_connection = db_connection
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Добавить билет')
        self.setGeometry(100, 100, 400, 400)

        layout = QVBoxLayout()

        self.existing_viewer_radio = QRadioButton('Выбрать существующего зрителя')
        self.new_viewer_radio = QRadioButton('Добавить нового зрителя')
        self.new_viewer_radio.setChecked(True)

        self.button_group = QButtonGroup()
        self.button_group.addButton(self.existing_viewer_radio)
        self.button_group.addButton(self.new_viewer_radio)
        self.button_group.buttonClicked.connect(self.toggle_viewer_option)

        self.existing_viewer_combobox = QComboBox()
        self.load_existing_viewers()
        self.existing_viewer_combobox.setVisible(False)

        self.name_label = QLabel('Имя:')
        self.name_entry = QLineEdit()

        self.email_label = QLabel('Email:')
        self.email_entry = QLineEdit()

        self.phone_label = QLabel('Номер телефона:')
        self.phone_entry = QLineEdit()

        self.movie_label = QLabel('Фильм:')
        self.movie_combobox = QComboBox()
        self.load_movies()

        self.session_label = QLabel('Сеанс:')
        self.session_combobox = QComboBox()
        self.movie_combobox.currentIndexChanged.connect(self.load_sessions)

        self.seat_label = QLabel('Номер места:')
        self.seat_combobox = QComboBox()

        add_button = QPushButton('Добавить билет')
        add_button.clicked.connect(self.add_ticket)

        layout.addWidget(self.existing_viewer_radio)
        layout.addWidget(self.existing_viewer_combobox)
        layout.addWidget(self.new_viewer_radio)
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_entry)
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_entry)
        layout.addWidget(self.phone_label)
        layout.addWidget(self.phone_entry)
        layout.addWidget(self.movie_label)
        layout.addWidget(self.movie_combobox)
        layout.addWidget(self.session_label)
        layout.addWidget(self.session_combobox)
        layout.addWidget(self.seat_label)
        layout.addWidget(self.seat_combobox)
        layout.addWidget(add_button)

        self.setLayout(layout)
        self.toggle_viewer_option()

    def toggle_viewer_option(self):
        if self.existing_viewer_radio.isChecked():
            self.existing_viewer_combobox.setVisible(True)
            self.name_label.setVisible(False)
            self.name_entry.setVisible(False)
            self.email_label.setVisible(False)
            self.email_entry.setVisible(False)
            self.phone_label.setVisible(False)
            self.phone_entry.setVisible(False)
        else:
            self.existing_viewer_combobox.setVisible(False)
            self.name_label.setVisible(True)
            self.name_entry.setVisible(True)
            self.email_label.setVisible(True)
            self.email_entry.setVisible(True)
            self.phone_label.setVisible(True)
            self.phone_entry.setVisible(True)

    def load_existing_viewers(self):
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT viewer_id, name FROM viewers')
        viewers = cursor.fetchall()
        for viewer in viewers:
            self.existing_viewer_combobox.addItem(viewer[1], viewer[0])

    def load_movies(self):
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT movie_id, title FROM movies')
        movies = cursor.fetchall()
        for movie in movies:
            self.movie_combobox.addItem(movie[1], movie[0])

    def load_sessions(self):
        self.session_combobox.clear()
        movie_id = self.movie_combobox.currentData()
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT session_id, session_time FROM sessions WHERE movie_id = %s', (movie_id,))
        sessions = cursor.fetchall()
        for session in sessions:
            session_time_str = session[1].strftime('%Y-%m-%d %H:%M')  # Преобразование datetime в строку
            self.session_combobox.addItem(session_time_str, session[0])
        self.load_available_seats()

    def load_available_seats(self):
        self.seat_combobox.clear()
        session_id = self.session_combobox.currentData()
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT seat_number FROM tickets WHERE session_id = %s', (session_id,))
        occupied_seats = cursor.fetchall()
        occupied_seat_numbers = {seat[0] for seat in occupied_seats}
        available_seats = [str(i) for i in range(1, 301) if str(i) not in occupied_seat_numbers]
        self.seat_combobox.addItems(available_seats)

    def add_ticket(self):
        movie_id = self.movie_combobox.currentData()
        session_id = self.session_combobox.currentData()
        seat_number = self.seat_combobox.currentText()

        cursor = self.db_connection.cursor()

        # Получение названия фильма
        cursor.execute('SELECT title FROM movies WHERE movie_id = %s', (movie_id,))
        movie_title = cursor.fetchone()[0]

        # Получение цены билета и ID зала из сеанса
        cursor.execute('SELECT ticket_price, hall_id FROM sessions WHERE session_id = %s', (session_id,))
        session_data = cursor.fetchone()
        ticket_price = session_data[0]
        hall_id = session_data[1]

        if self.existing_viewer_radio.isChecked():
            viewer_id = self.existing_viewer_combobox.currentData()
        else:
            name = self.name_entry.text()
            email = self.email_entry.text()
            phone = self.phone_entry.text()

            # Проверка, существует ли уже зритель с таким email
            cursor.execute('SELECT viewer_id FROM viewers WHERE email = %s', (email,))
            viewer = cursor.fetchone()

            if viewer:
                viewer_id = viewer[0]
            else:
                cursor.execute('INSERT INTO viewers (name, email, phone_number) VALUES (%s, %s, %s) RETURNING viewer_id',
                               (name, email, phone))
                viewer_id = cursor.fetchone()[0]

        cursor.execute('INSERT INTO tickets (session_id, viewer_id, movie_id, title, seat_number, purchase_time, ticket_price, hall_id) VALUES (%s, %s, %s, %s, %s, NOW(), %s, %s)',
                       (session_id, viewer_id, movie_id, movie_title, seat_number, ticket_price, hall_id))
        self.db_connection.commit()
        QMessageBox.information(self, 'Добавить билет', 'Билет успешно добавлен!')

        self.parent.populate_table()  # Обновление таблицы после добавления билета
        self.close()




class ViewTicketsWindow(QWidget):
    def __init__(self, db_connection):
        super().__init__()

        self.db_connection = db_connection
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Посмотреть билеты')
        self.setWindowIcon(QIcon('icons/tickets.png'))
        self.setGeometry(100, 100, 1000, 600)

        layout = QVBoxLayout()

        self.table_label = QLabel('Билеты:')
        self.table_widget = QTableWidget(self)

        # Добавляем выпадающий список для выбора зала
        self.hall_combobox = QComboBox()
        self.hall_combobox.addItem('Все Залы', None)
        self.load_halls()

        add_ticket_button = QPushButton('Новый Билет')
        add_ticket_button.setIcon(QIcon('icons/add.png'))
        add_ticket_button.clicked.connect(self.show_add_ticket_window)

        self.to_pdf_button = QPushButton('В PDF')
        self.to_pdf_button.setIcon(QIcon('icons/pdf.png'))
        self.to_pdf_button.clicked.connect(self.generate_pdf)

        delete_ticket_button = QPushButton('Удалить билет')
        delete_ticket_button.setIcon(QIcon('icons/delete.png'))
        delete_ticket_button.clicked.connect(self.delete_ticket)

        # Добавляем элементы в layout
        layout.addWidget(self.table_label)
        layout.addWidget(self.hall_combobox)  # Добавляем выпадающий список зала в layout
        layout.addWidget(self.table_widget)
        layout.addWidget(add_ticket_button)
        layout.addWidget(self.to_pdf_button)
        layout.addWidget(delete_ticket_button)

        self.setLayout(layout)

        self.hall_combobox.currentIndexChanged.connect(self.populate_table)  # Обновляем таблицу при изменении выбора зала

        self.populate_table()

    def load_halls(self):
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT hall_id, hall_name FROM halls')
        halls = cursor.fetchall()
        for hall in halls:
            self.hall_combobox.addItem(hall[1], hall[0])

    def populate_table(self):
        cursor = self.db_connection.cursor()
        hall_id = self.hall_combobox.currentData()

        query = 'SELECT * FROM tickets'
        params = []

        if hall_id is not None:
            query += ' WHERE hall_id = %s'
            params.append(hall_id)
        
        cursor.execute(query, tuple(params))
        tickets = cursor.fetchall()

        self.table_widget.setRowCount(len(tickets))
        self.table_widget.setColumnCount(9)
        self.table_widget.setHorizontalHeaderLabels(['ID Билета', 'ID Сеанса', 'ID Зрителя', 'ID Фильма', 'Название фильма', 'Номер места', 'Время покупки', 'Цена билета', 'ID Зала'])

        for row, ticket in enumerate(tickets):
            for col, data in enumerate(ticket):
                item = QTableWidgetItem(str(data))
                self.table_widget.setItem(row, col, item)

    def show_add_ticket_window(self):
        self.add_ticket_window = AddTicketWindow(self.db_connection, self)
        self.add_ticket_window.show()

    def generate_pdf(self):
        current_row = self.table_widget.currentRow()
        if current_row > -1:
            ticket_data = []
            for col in range(self.table_widget.columnCount()):
                item = self.table_widget.item(current_row, col)
                ticket_data.append(item.text())

            ticket_id = ticket_data[0]
            movie_title = ticket_data[4]
            hall_id = ticket_data[8]
            seat_number = ticket_data[5]
            purchase_time = ticket_data[6]
            ticket_price = ticket_data[7]

            # Получение URL постера из таблицы movies
            movie_id = ticket_data[3]
            cursor = self.db_connection.cursor()
            cursor.execute('SELECT poster_url FROM movies WHERE movie_id = %s', (movie_id,))
            poster_url = cursor.fetchone()[0]

            # Создание PDF
            pdf_file = "ticket.pdf"
            doc = SimpleDocTemplate(pdf_file, pagesize=letter)
            story = []

            # Регистрация шрифта
            pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
            pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSansBold.ttf'))

            styles = getSampleStyleSheet()
            styles['Normal'].fontName = 'DejaVuSans'
            styles['Heading1'].fontName = 'DejaVuSans-Bold'

            # Добавление логотипа
            logo_path = 'logoc.png'
            logo = Image(logo_path, width=150, height=52)
            story.append(logo)
            story.append(Spacer(1, 12))

            # Заголовок
            story.append(Paragraph("Карточка-билет", styles['Heading1']))
            story.append(Spacer(1, 12))

            # Информация о билете
            info_text = [
                f"Билет #: {ticket_id}",
                f"Название Фильма: {movie_title}",
                f"Зал #: {hall_id}",
                f"Номер места: {seat_number}",
                f"Время покупки: {purchase_time}",
                f"Цена билета: {ticket_price}"
            ]

            for line in info_text:
                story.append(Paragraph(line, styles['Normal']))
                story.append(Spacer(1, 12))

            # Загрузка и добавление постера
            try:
                response = requests.get(poster_url)
                response.raise_for_status()
                image_stream = io.BytesIO(response.content)
                image = Image(image_stream, width=150, height=200)
                story.append(image)
            except requests.RequestException:
                story.append(Paragraph("Не удалось загрузить изображение постера.", styles['Normal']))

            doc.build(story)

            # Открытие PDF файла
            self.open_pdf(pdf_file)

    def delete_ticket(self):
        current_row = self.table_widget.currentRow()
        if current_row > -1:
            ticket_data = []
            for col in range(self.table_widget.columnCount()):
                item = self.table_widget.item(current_row, col)
                ticket_data.append(item.text())

            ticket_id = int(ticket_data[0])  # Преобразование в int
            session_id = int(ticket_data[1])  # Преобразование в int
            viewer_id = int(ticket_data[2])  # Преобразование в int
            movie_id = int(ticket_data[3])  # Преобразование в int
            title = ticket_data[4]
            seat_number = int(ticket_data[5])  # Преобразование в int
            purchase_time = ticket_data[6]
            ticket_price = float(ticket_data[7])  # Преобразование в float
            hall_id = int(ticket_data[8])  # Преобразование в int

            cursor = self.db_connection.cursor()

            try:
                # Перенос данных в таблицу tickets_archive
                cursor.execute('''
                    INSERT INTO tickets_archive (ticket_id, session_id, viewer_id, movie_id, title, seat_number, purchase_time, ticket_price, hall_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (ticket_id, session_id, viewer_id, movie_id, title, seat_number, purchase_time, ticket_price, hall_id))

                # Удаление записи из таблицы tickets
                cursor.execute('DELETE FROM tickets WHERE ticket_id = %s', (ticket_id,))

                self.db_connection.commit()
                self.populate_table()
                QMessageBox.information(self, 'Удалить билет', 'Билет успешно удален и перемещен в архив!')

            except Exception as e:
                self.db_connection.rollback()
                QMessageBox.critical(self, 'Ошибка', f'Ошибка при удалении билета: {str(e)}')

    def open_pdf(self, file_path):
        dialog = QDialog(self)
        dialog.setWindowTitle("Просмотр PDF")
        layout = QVBoxLayout()
        label = QLabel(dialog)
        label.setText(f"PDF файл создан: {file_path}")
        layout.addWidget(label)
        dialog.setLayout(layout)
        dialog.finished.connect(lambda: self.open_pdf_in_os(file_path))
        dialog.exec_()

    def open_pdf_in_os(self, file_path):
        try:
            if os.name == 'posix':
                os.system(f'open "{file_path}"')
            elif os.name == 'nt':
                os.startfile(file_path)
            else:
                QMessageBox.information(self, "Ошибка", "Не поддерживаемая операционная система.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть PDF файл: {str(e)}")





class ViewViewersWindow(QWidget):
    def __init__(self, db_connection):
        super().__init__()

        self.db_connection = db_connection
        self.sort_order = Qt.AscendingOrder  # Начальная сортировка по возрастанию
        self.column_sort_states = {}  # Словарь для отслеживания состояний сортировки каждого столбца
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Просмотр зрителей')
        self.setGeometry(100, 100, 800, 400)

        layout = QVBoxLayout()

        self.table_label = QLabel('Зрители:')
        self.table_widget = QTableWidget(self)
        self.table_widget.setSortingEnabled(True)  # Включаем возможность сортировки

        purchased_tickets_button = QPushButton('Купленные билеты')
        purchased_tickets_button.clicked.connect(self.generate_purchased_tickets_pdf)

        layout.addWidget(self.table_label)
        layout.addWidget(self.table_widget)
        layout.addWidget(purchased_tickets_button)

        self.setLayout(layout)
        self.populate_table()

        # Подключаем сигнал клика по заголовку к слоту сортировки
        self.table_widget.horizontalHeader().sectionClicked.connect(self.sort_by_column)

    def populate_table(self):
        cursor = self.db_connection.cursor()
        query = '''
            SELECT v.viewer_id, v.name, v.email, v.phone_number, COUNT(t.ticket_id) AS ticket_count
            FROM viewers v
            LEFT JOIN tickets t ON v.viewer_id = t.viewer_id
            GROUP BY v.viewer_id, v.name, v.email, v.phone_number
        '''
        cursor.execute(query)
        viewers = cursor.fetchall()

        self.table_widget.setRowCount(len(viewers))
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(['ID Зрителя', 'Имя', 'Email', 'Номер телефона', 'Кол-во купленных билетов'])

        for row, viewer in enumerate(viewers):
            for col, data in enumerate(viewer):
                item = QTableWidgetItem(str(data))
                self.table_widget.setItem(row, col, item)

    def sort_by_column(self, column_index):
        # Проверяем текущее состояние сортировки для этого столбца и переключаем его
        if column_index in self.column_sort_states and self.column_sort_states[column_index] == Qt.AscendingOrder:
            self.column_sort_states[column_index] = Qt.DescendingOrder
        else:
            self.column_sort_states[column_index] = Qt.AscendingOrder

        # Сортируем таблицу по выбранному столбцу и направлению
        self.table_widget.sortItems(column_index, self.column_sort_states[column_index])

    def generate_purchased_tickets_pdf(self):
        current_row = self.table_widget.currentRow()
        if current_row > -1:
            viewer_id = int(self.table_widget.item(current_row, 0).text())
            viewer_name = self.table_widget.item(current_row, 1).text()

            cursor = self.db_connection.cursor()
            cursor.execute('''
                SELECT t.ticket_id, m.title, s.hall_id, t.seat_number, t.purchase_time, t.ticket_price
                FROM tickets t
                JOIN movies m ON t.movie_id = m.movie_id
                JOIN sessions s ON t.session_id = s.session_id
                WHERE t.viewer_id = %s
            ''', (viewer_id,))
            tickets = cursor.fetchall()

            if tickets:
                # Создание PDF
                pdf_file = "purchased_tickets.pdf"
                doc = SimpleDocTemplate(pdf_file, pagesize=landscape(letter))
                story = []

                # Регистрация шрифта DejaVu Sans для поддержки кириллицы
                pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
                pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSansBold.ttf'))

                styles = getSampleStyleSheet()
                styles['Normal'].fontName = 'DejaVuSans'
                styles['Heading1'].fontName = 'DejaVuSans-Bold'
                styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))

                # Заголовок
                story.append(Paragraph(f"Купленные билеты зрителя: {viewer_name}", styles['Heading1']))
                story.append(Spacer(1, 12))

                # Данные для таблицы
                table_data = [
                    [Paragraph('<b>Билет #</b>', styles['Normal']),
                     Paragraph('<b>Название Фильма</b>', styles['Normal']),
                     Paragraph('<b>Зал #</b>', styles['Normal']),
                     Paragraph('<b>Номер места</b>', styles['Normal']),
                     Paragraph('<b>Время покупки</b>', styles['Normal']),
                     Paragraph('<b>Цена билета</b>', styles['Normal'])]
                ]

                for ticket in tickets:
                    table_data.append([
                        Paragraph(str(ticket[0]), styles['Normal']),
                        Paragraph(str(ticket[1]), styles['Normal']),
                        Paragraph(str(ticket[2]), styles['Normal']),
                        Paragraph(str(ticket[3]), styles['Normal']),
                        Paragraph(str(ticket[4]), styles['Normal']),
                        Paragraph(str(ticket[5]), styles['Normal'])
                    ])

                # Создание таблицы
                table = Table(table_data, colWidths=[1.5 * inch] * 6)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
                    ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))

                story.append(table)
                doc.build(story)

                # Открытие PDF файла
                self.open_pdf(pdf_file)
            else:
                QMessageBox.information(self, 'Купленные билеты', 'У выбранного зрителя нет купленных билетов.')

    def open_pdf(self, file_path):
        dialog = QDialog(self)
        dialog.setWindowTitle("Просмотр PDF")
        layout = QVBoxLayout()
        label = QLabel(dialog)
        label.setText(f"PDF файл создан: {file_path}")
        layout.addWidget(label)
        dialog.setLayout(layout)
        dialog.finished.connect(lambda: self.open_pdf_in_os(file_path))
        dialog.exec_()

    def open_pdf_in_os(self, file_path):
        try:
            if os.name == 'posix':
                os.system(f'open "{file_path}"')
            elif os.name == 'nt':
                os.startfile(file_path)
            else:
                QMessageBox.information(self, "Ошибка", "Не поддерживаемая операционная система.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть PDF файл: {str(e)}")






if __name__ == '__main__':
    app = QApplication(sys.argv)

    db_connection = psycopg2.connect(
        database='cinema',
        user='postgres',
        password='p@ssw0rd',
        host='127.0.0.1',
        port='5432'
    )

    registration_window = RegistrationWindow(db_connection)
    view_movies_window = ViewMoviesWindow(db_connection)
    add_movie_window = AddMovieWindow(db_connection, user_id=None)
    view_promotions_window = ViewPromotionsWindow(db_connection)
    view_users_window = ViewUsersWindow(db_connection)
    view_sessions_window = ViewSessionsWindow(db_connection)
    create_session_window = CreateSessionWindow(db_connection)  # Новый экземпляр окна создания сеанса
    view_tickets_window = ViewTicketsWindow(db_connection)  # Новый экземпляр окна просмотра билетов
    add_ticket_window = AddTicketWindow(db_connection, view_tickets_window)  # Новый экземпляр окна добавления билета
    view_viewers_window = ViewViewersWindow(db_connection)  # Новый экземпляр окна просмотра зрителей
    login_window = LoginWindow(db_connection, registration_window, view_movies_window, add_movie_window, view_promotions_window, view_users_window, view_sessions_window, view_tickets_window, view_viewers_window)
    
    login_window.view_sessions_window = view_sessions_window  # Присваиваем экземпляр
    login_window.view_tickets_window = view_tickets_window  # Присваиваем экземпляр
    login_window.view_viewers_window = view_viewers_window  # Присваиваем экземпляр

    login_window.show()
    sys.exit(app.exec_())

