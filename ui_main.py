import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QTabWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QListWidget, QPushButton, 
                             QLineEdit, QTextEdit, QRadioButton, QButtonGroup, 
                             QMessageBox, QFileDialog, QFormLayout, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PIL import Image  # Интеграция Pillow
from database import QuizDatabase

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = QuizDatabase()
        self.current_test_questions = []
        self.current_question_index = 0
        self.score = 0
        self.selected_image_path = ""
        
        self._setup_ui()
        self._bind_signals()
        self._refresh_test_lists()

    def _setup_ui(self):
        """Инициализация интерфейса (без использования сеток hardcode размеров)."""
        self.setWindowTitle("Система тестирования PyQt5")
        self.setMinimumSize(950, 700)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tab_run = QWidget()
        self.layout_run = QVBoxLayout(self.tab_run)
        
        self.run_list_widget = QWidget()
        self.layout_run_list = QVBoxLayout(self.run_list_widget)
        self.lbl_select_test = QLabel("Выберите тест из списка для начала прохождения:")
        self.lbl_select_test.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.list_available_tests = QListWidget()
        self.btn_start_test = QPushButton("Начать прохождение")
        self.layout_run_list.addWidget(self.lbl_select_test)
        self.layout_run_list.addWidget(self.list_available_tests)
        self.layout_run_list.addWidget(self.btn_start_test)
        
        self.run_process_widget = QWidget()
        self.run_process_widget.setVisible(False)
        self.layout_process = QVBoxLayout(self.run_process_widget)
        
        self.lbl_q_text = QLabel("Текст вопроса")
        self.lbl_q_text.setWordWrap(True)
        self.lbl_q_text.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.lbl_q_image = QLabel() 
        self.lbl_q_image.setAlignment(Qt.AlignCenter)
        
        self.answers_group_box = QGroupBox("Варианты ответа:")
        self.layout_answers = QVBoxLayout(self.answers_group_box)
        self.radio_buttons = []
        self.btn_group = QButtonGroup(self)
        
        for i in range(4):
            rb = QRadioButton()
            self.radio_buttons.append(rb)
            self.btn_group.addButton(rb, i)
            self.layout_answers.addWidget(rb)
            
        self.btn_next_question = QPushButton("Дальше")
        self.layout_process.addWidget(self.lbl_q_text)
        self.layout_process.addWidget(self.lbl_q_image)
        self.layout_process.addWidget(self.answers_group_box)
        self.layout_process.addWidget(self.btn_next_question)

        self.layout_run.addWidget(self.run_list_widget)
        self.layout_run.addWidget(self.run_process_widget)
        self.tabs.addTab(self.tab_run, "📝 Прохождение тестов")

        self.tab_edit = QWidget()
        self.layout_edit = QHBoxLayout(self.tab_edit)

        self.left_panel = QWidget()
        self.layout_left = QVBoxLayout(self.left_panel)
        self.layout_left.addWidget(QLabel("Доступные тесты:"))
        self.list_edit_tests = QListWidget()
        self.layout_left.addWidget(self.list_edit_tests)
        
        self.btn_delete_test = QPushButton("Удалить выбранный тест")
        self.btn_delete_test.setStyleSheet("background-color: #ff4d4d; color: white;")
        self.layout_left.addWidget(self.btn_delete_test)
        
        self.group_create_test = QGroupBox("Создать новый тест")
        self.form_test = QFormLayout(self.group_create_test)
        self.entry_test_title = QLineEdit()
        self.entry_test_desc = QLineEdit()
        self.btn_save_test = QPushButton("Добавить тест")
        self.form_test.addRow("Название:", self.entry_test_title)
        self.form_test.addRow("Описание:", self.entry_test_desc)
        self.form_test.addRow(self.btn_save_test)
        self.layout_left.addWidget(self.group_create_test)
        
        self.layout_edit.addWidget(self.left_panel, stretch=1)

        self.right_panel = QGroupBox("Редактор вопросов для выбранного теста")
        self.layout_right = QVBoxLayout(self.right_panel)
        
        self.form_question = QFormLayout()
        self.entry_q_text = QTextEdit()
        self.entry_q_text.setMaximumHeight(60)
        
        self.layout_img_select = QHBoxLayout()
        self.lbl_img_status = QLabel("Изображение не выбрано")
        self.btn_select_img = QPushButton("Обзор...")
        self.layout_img_select.addWidget(self.lbl_img_status)
        self.layout_img_select.addWidget(self.btn_select_img)
        
        self.entry_answers = []
        self.radio_correct = []
        self.ans_button_group = QButtonGroup(self)
        
        self.form_question.addRow("Текст вопроса:", self.entry_q_text)
        self.form_question.addRow("Изображение (опция):", self.layout_img_select)
        
        for i in range(4):
            h_box = QHBoxLayout()
            le = QLineEdit()
            rb = QRadioButton("Верный")
            if i == 0: rb.setChecked(True)
            self.entry_answers.append(le)
            self.radio_correct.append(rb)
            self.ans_button_group.addButton(rb, i)
            h_box.addWidget(le, stretch=4)
            h_box.addWidget(rb, stretch=1)
            self.form_question.addRow(f"Вариант {i+1}:", h_box)
            
        self.btn_save_question = QPushButton("Сохранить вопрос в тест")
        self.btn_save_question.setStyleSheet("background-color: #4CAF50; color: white;")
        self.form_question.addRow(self.btn_save_question)
        
        self.layout_right.addLayout(self.form_question)
        self.layout_edit.addWidget(self.right_panel, stretch=2)
        
        self.tabs.addTab(self.tab_edit, "🛠 Конструктор тестов")

    def _bind_signals(self):
        """Привязка обработчиков сигналов строго через .connect()."""
        self.btn_save_test.clicked.connect(self._slots_add_test)
        self.btn_delete_test.clicked.connect(self._slots_delete_test)
        self.btn_select_img.clicked.connect(self._slots_select_image)
        self.btn_save_question.clicked.connect(self._slots_add_question)
        self.btn_start_test.clicked.connect(self._slots_start_testing)
        self.btn_next_question.clicked.connect(self._slots_next_question)

    def _refresh_test_lists(self):
        """Обновление списков тестов на обеих вкладках."""
        self.list_available_tests.clear()
        self.list_edit_tests.clear()
        tests = self.db.get_all_tests()
        for t_id, title, desc in tests:
            display_text = f"[{t_id}] {title} — {desc}"
            self.list_available_tests.addItem(display_text)
            self.list_edit_tests.addItem(display_text)

    def _slots_add_test(self):
        title = self.entry_test_title.text().strip()
        desc = self.entry_test_desc.text().strip()
        if not title:
            QMessageBox.warning(self, "Валидация", "Название теста не может быть пустым!")
            return
        self.db.add_test(title, desc)
        self.entry_test_title.clear()
        self.entry_test_desc.clear()
        self._refresh_test_lists()

    def _slots_delete_test(self):
        selected = self.list_edit_tests.currentItem()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите тест для удаления!")
            return
        test_id = int(selected.text().split("]")[0].replace("[", ""))
        self.db.delete_test(test_id)
        self._refresh_test_lists()

    def _slots_select_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выбрать картинку к вопросу", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.selected_image_path = path
            self.lbl_img_status.setText(os.path.basename(path))

    def _slots_add_question(self):
        selected = self.list_edit_tests.currentItem()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите тест в левом списке!")
            return
        test_id = int(selected.text().split("]")[0].replace("[", ""))
        q_text = self.entry_q_text.toPlainText().strip()
        
        if not q_text:
            QMessageBox.warning(self, "Валидация", "Введите текст вопроса!")
            return
            
        answers_list = []
        for i in range(4):
            ans_t = self.entry_answers[i].text().strip()
            if not ans_t:
                QMessageBox.warning(self, "Валидация", f"Заполните вариант ответа {i+1}!")
                return
            is_corr = 1 if self.radio_correct[i].isChecked() else 0
            answers_list.append((ans_t, is_corr))

        success = self.db.add_question_with_answers(test_id, q_text, self.selected_image_path, answers_list)
        if success:
            QMessageBox.information(self, "Успех", "Вопрос успешно добавлен в тест!")
            self.entry_q_text.clear()
            self.selected_image_path = ""
            self.lbl_img_status.setText("Изображение не выбрано")
            for le in self.entry_answers: le.clear()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось сохранить вопрос.")

    def _slots_start_testing(self):
        selected = self.list_available_tests.currentItem()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите тест из списка!")
            return
        test_id = int(selected.text().split("]")[0].replace("[", ""))
        self.current_test_questions = self.db.get_test_data(test_id)
        
        if not self.current_test_questions:
            QMessageBox.warning(self, "Ошибка", "В этом тесте пока нет вопросов!")
            return
            
        self.current_question_index = 0
        self.score = 0
        self.run_list_widget.setVisible(False)
        self.run_process_widget.setVisible(True)
        self._display_question()

    def _display_question(self):
        qdata = self.current_test_questions[self.current_question_index]
        self.lbl_q_text.setText(f"Вопрос {self.current_question_index + 1}: {qdata['text']}")
        
        if qdata['image'] and os.path.exists(qdata['image']):
            try:
                with Image.open(qdata['image']) as img:
                    img.thumbnail((350, 250))
                    os.makedirs("assets", exist_ok=True)
                    temp_path = "assets/temp_thumb.png"
                    img.save(temp_path)
                    self.lbl_q_image.setPixmap(QPixmap(temp_path))
                    self.lbl_q_image.setVisible(True)
            except Exception:
                self.lbl_q_image.setText("[Ошибка загрузки изображения Pillow]")
        else:
            self.lbl_q_image.setVisible(False)

        for i, ans in enumerate(qdata['answers']):
            self.radio_buttons[i].setText(ans[0])
            self.radio_buttons[i].setChecked(i == 0)

    def _slots_next_question(self):
        qdata = self.current_test_questions[self.current_question_index]
        selected_idx = self.btn_group.checkedId()
        
        if qdata['answers'][selected_idx][1] == 1:
            self.score += 1
            
        self.current_question_index += 1
        if self.current_question_index < len(self.current_test_questions):
            self._display_question()
        else:
            QMessageBox.information(self, "Результат", 
                                    f"Тестирование завершено!\nВы набрали: {self.score} из {len(self.current_test_questions)} баллов.")
            self.run_process_widget.setVisible(False)
            self.run_list_widget.setVisible(True)
            self._refresh_test_lists()

    def closeEvent(self, event):
        """Безопасное закрытие приложения с подтверждением."""
        reply = QMessageBox.question(self, 'Выход', "Вы действительно хотите закрыть приложение?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()