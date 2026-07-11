import sys
from PyQt5.QtWidgets import QApplication
from ui_main import MainWindow 

def main():
    app = QApplication(sys.argv)
    
    app.setStyleSheet("""
        QMainWindow { background-color: ##fafafa; }
        QPushButton { 
            font-size: 13px; font-weight: bold; padding: 6px 12px; 
            border-radius: 4px; min-height: 25px; background-color: #0078D4; color: white;
        }
        QPushButton:hover { background-color: #005A9E; }
        QGroupBox { font-weight: bold; border: 1px solid #cccccc; border-radius: 6px; margin-top: 12px; }
        QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }
        QLineEdit, QTextEdit { border: 1px solid #cccccc; border-radius: 4px; padding: 4px; background: white; }
        QTabWidget::pane { border: 1px solid #cccccc; }
        QTabBar::tab { background: #e1e1e1; padding: 8px 20px; border-top-left-radius: 4px; border-top-right-radius: 4px; }
        QTabBar::tab:selected { background: white; border-bottom-color: none; font-weight: bold; }
    """)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()