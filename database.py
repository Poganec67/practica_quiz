import sqlite3
import os

class QuizDatabase:
    def __init__(self, db_name="quiz.db"):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        """Безопасное подключение к БД с обработкой исключений."""
        try:
            return sqlite3.connect(self.db_name)
        except sqlite3.Error as e:
            print(f"Ошибка подключения к базе данных: {e}")
            return None

    def init_db(self):
        """Инициализация структуры таблиц."""
        conn = self.get_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            # Включаем поддержку каскадного удаления
            cursor.execute("PRAGMA foreign_keys = ON;")
            
            # Таблица тестов
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT
                )
            """)
            # Таблица вопросов
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_id INTEGER NOT NULL,
                    question_text TEXT NOT NULL,
                    image_path TEXT,
                    FOREIGN KEY (test_id) REFERENCES tests (id) ON DELETE CASCADE
                )
            """)
            # Таблица ответов
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question_id INTEGER NOT NULL,
                    answer_text TEXT NOT NULL,
                    is_correct INTEGER NOT NULL,
                    FOREIGN KEY (question_id) REFERENCES questions (id) ON DELETE CASCADE
                )
            """)
            conn.commit()
        except sqlite3.Error as e:
            print(f"Ошибка при создании таблиц: {e}")
        finally:
            conn.close()

    # --- CRUD для Тестов ---
    def add_test(self, title, description):
        conn = self.get_connection()
        if not conn: return None
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tests (title, description) VALUES (?, ?)", (title, description))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error:
            return None
        finally: conn.close()

    def get_all_tests(self):
        conn = self.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, description FROM tests")
            return cursor.fetchall()
        except sqlite3.Error:
            return []
        finally: conn.close()

    def delete_test(self, test_id):
        conn = self.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tests WHERE id = ?", (test_id,))
            conn.commit()
            return True
        except sqlite3.Error:
            return False
        finally: conn.close()

    # --- CRUD для Вопросов и Ответов ---
    def add_question_with_answers(self, test_id, q_text, image_path, answers_list):
        """Комплексное добавление вопроса и вариантов ответов в одной транзакции."""
        conn = self.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO questions (test_id, question_text, image_path) VALUES (?, ?, ?)",
                           (test_id, q_text, image_path))
            question_id = cursor.lastrowid

            for ans_text, is_corr in answers_list:
                cursor.execute("INSERT INTO answers (question_id, answer_text, is_correct) VALUES (?, ?, ?)",
                               (question_id, ans_text, is_corr))
            conn.commit()
            return True
        except sqlite3.Error:
            conn.rollback()
            return False
        finally: conn.close()

    def get_test_data(self, test_id):
        """Получение всех вопросов и ответов для прохождения теста."""
        conn = self.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, question_text, image_path FROM questions WHERE test_id = ?", (test_id,))
            questions = cursor.fetchall()
            
            full_data = []
            for q_id, q_text, img_path in questions:
                cursor.execute("SELECT answer_text, is_correct FROM answers WHERE question_id = ?", (q_id,))
                answers = cursor.fetchall()
                full_data.append({
                    "id": q_id,
                    "text": q_text,
                    "image": img_path,
                    "answers": answers
                })
            return full_data
        except sqlite3.Error:
            return []
        finally: conn.close()