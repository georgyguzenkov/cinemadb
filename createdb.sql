-- Создание имени базы данных
CREATE DATABASE cinema;

-- Создание таблицы пользователей
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- Создание таблицы ролей пользователей
CREATE TABLE user_roles (
    role_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    role VARCHAR(255) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Создание таблицы фильмов
CREATE TABLE movies (
    movie_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    release_date DATE NOT NULL,
    genre VARCHAR(255) NOT NULL,
    duration_minutes INTEGER NOT NULL,
    description TEXT,
    poster_url TEXT,
    actors TEXT,
    hall_id INTEGER,
    ticket_price NUMERIC(10, 2),
    session_time TIMESTAMP
);

-- Создание таблицы залов
CREATE TABLE halls (
    hall_id SERIAL PRIMARY KEY,
    hall_name VARCHAR(255) NOT NULL
);

-- Создание таблицы сеансов
CREATE TABLE sessions (
    session_id SERIAL PRIMARY KEY,
    movie_id INTEGER NOT NULL,
    hall_id INTEGER NOT NULL,
    session_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    ticket_price NUMERIC(10, 2),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
    FOREIGN KEY (hall_id) REFERENCES halls(hall_id)
);

-- Создание таблицы зрителей
CREATE TABLE viewers (
    viewer_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone_number VARCHAR(255)
);

-- Создание таблицы билетов
CREATE TABLE tickets (
    ticket_id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL,
    viewer_id INTEGER NOT NULL,
    movie_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    seat_number VARCHAR(255) NOT NULL,
    purchase_time TIMESTAMP DEFAULT NOW(),
    ticket_price NUMERIC(10, 2),
    hall_id INTEGER,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id),
    FOREIGN KEY (viewer_id) REFERENCES viewers(viewer_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
    FOREIGN KEY (hall_id) REFERENCES halls(hall_id)
);

-- Создание таблицы промоакций
CREATE TABLE promotions (
    promo_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    discount_percentage NUMERIC(5, 2) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL
);

-- Создание таблицы архива билетов
CREATE TABLE tickets_archive (
    archive_id SERIAL PRIMARY KEY,
    ticket_id INTEGER,
    session_id INTEGER,
    viewer_id INTEGER,
    movie_id INTEGER,
    title VARCHAR(255),
    seat_number VARCHAR(255),
    purchase_time TIMESTAMP,
    ticket_price NUMERIC(10, 2),
    hall_id INTEGER
);
