import sys
import pdfplumber
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QTextEdit, QHBoxLayout, QProgressBar)
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt
from deepdiff import DeepDiff

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Function to extract and concatenate tables from a PDF file
def extract_tables_from_pdf(pdf_path):
    all_tables = pd.DataFrame()  # Initialize an empty DataFrame for concatenation
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages():
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    df = pd.DataFrame(table)
                    all_tables = pd.concat([all_tables, df], ignore_index=True)
    return all_tables

# PyQt5 UI Application
class EntityExtractorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.pdf1_data = None
        self.pdf2_data = None
        self.pdf1_tables = None
        self.pdf2_tables = None
        self.initUI()

    def initUI(self):
        # Main layout
        main_layout = QHBoxLayout(self)

        # Sidebar (in a widget to apply style)
        sidebar_widget = QWidget()
        sidebar = QVBoxLayout()
        sidebar_label = QLabel("PDF Comparison Tool\n\nDeveloped by: [Your Name]\n\nThis tool compares two PDFs based on text and tables extracted from them.")
        sidebar_label.setAlignment(Qt.AlignCenter)
        sidebar.addWidget(sidebar_label)
        sidebar_widget.setLayout(sidebar)

        # Styling for sidebar
        sidebar_widget.setStyleSheet("""
            background-color: #2C2F33;
            color: white;
            padding: 10px;
            border-radius: 10px;
        """)

        # Main content area
        content_layout = QVBoxLayout()

        # Label for instruction
        self.label = QLabel("Select two PDF files and compare data based on 'Name', 'NAME', 'Nama', 'name':")
        self.label.setStyleSheet("color: #61AFEF; font-size: 16px; font-weight: bold;")
        content_layout.addWidget(self.label)

        # Loading animation
        self.loading_label = QLabel()
        self.loading_movie = QMovie("loading.gif")
        self.loading_label.setMovie(self.loading_movie)
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setVisible(False)
        content_layout.addWidget(self.loading_label)

        # Buttons
        self.load_pdf1_btn = QPushButton("Load PDF 1", self)
        self.load_pdf1_btn.clicked.connect(self.load_pdf1)
        content_layout.addWidget(self.load_pdf1_btn)

        self.load_pdf2_btn = QPushButton("Load PDF 2", self)
        self.load_pdf2_btn.clicked.connect(self.load_pdf2)
        content_layout.addWidget(self.load_pdf2_btn)

        self.compare_btn = QPushButton("Compare PDFs and Save Delta", self)
        self.compare_btn.setEnabled(False)  # Disable until both PDFs are loaded
        self.compare_btn.clicked.connect(self.compare_tables)
        content_layout.addWidget(self.compare_btn)

        self.save_csv_pdf1_btn = QPushButton("Save CSV for PDF 1", self)
        self.save_csv_pdf1_btn.setEnabled(False)  # Disable until PDF 1 is loaded
        self.save_csv_pdf1_btn.clicked.connect(self.save_csv_pdf1)
        content_layout.addWidget(self.save_csv_pdf1_btn)

        self.save_csv_pdf2_btn = QPushButton("Save CSV for PDF 2", self)
        self.save_csv_pdf2_btn.setEnabled(False)  # Disable until PDF 2 is loaded
        self.save_csv_pdf2_btn.clicked.connect(self.save_csv_pdf2)
        content_layout.addWidget(self.save_csv_pdf2_btn)

        # Delta display
        self.delta_display = QTextEdit()
        self.delta_display.setReadOnly(True)
        self.delta_display.setStyleSheet("background-color: #282C34; color: #61AFEF; font-size: 14px;")
        content_layout.addWidget(self.delta_display)

        # Styling for buttons and layout
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(10)
        self.setStyleSheet("""
            QPushButton {
                background-color: #61AFEF;
                color: white;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:disabled {
                background-color: #ABB2BF;
            }
            QLabel {
                color: #61AFEF;
                font-size: 16px;
            }
        """)

        main_layout.addWidget(sidebar_widget, 1)
        main_layout.addLayout(content_layout, 3)

        self.setWindowTitle("Advanced PDF Comparison Tool")
        self.setGeometry(300, 100, 700, 500)

    def show_loading(self, is_loading=True):
        self.loading_label.setVisible(is_loading)
        if is_loading:
            self.loading_movie.start()
        else:
            self.loading_movie.stop()

    def load_pdf1(self):
        options = QFileDialog.Options()
        pdf_path, _ = QFileDialog.getOpenFileName(self, "Open PDF 1", "", "PDF Files (*.pdf)", options=options)
        
        if pdf_path:
            self.show_loading(True)
            self.pdf1_tables = extract_tables_from_pdf(pdf_path)
            self.show_loading(False)
            if not self.pdf1_tables.empty:
                self.save_csv_pdf1_btn.setEnabled(True)
                if self.pdf2_tables is not None:
                    self.compare_btn.setEnabled(True)

    def load_pdf2(self):
        options = QFileDialog.Options()
        pdf_path, _ = QFileDialog.getOpenFileName(self, "Open PDF 2", "", "PDF Files (*.pdf)", options=options)
        
        if pdf_path:
            self.show_loading(True)
            self.pdf2_tables = extract_tables_from_pdf(pdf_path)
            self.show_loading(False)
            if not self.pdf2_tables.empty:
                self.save_csv_pdf2_btn.setEnabled(True)
                if self.pdf1_tables is not None:
                    self.compare_btn.setEnabled(True)

    def compare_tables(self):
        if self.pdf1_tables.empty or self.pdf2_tables.empty:
            QMessageBox.warning(self, "Error", "Please load both PDFs before comparing.")
            return

        self.show_loading(True)
        delta = DeepDiff(self.pdf1_tables.to_dict(), self.pdf2_tables.to_dict(), ignore_order=True).to_dict()
        self.show_loading(False)

        if not delta:
            self.delta_display.setText("The two PDFs have no differences.")
        else:
            self.delta_display.setText(str(delta))

    def save_csv_pdf1(self):
        if self.pdf1_tables.empty:
            QMessageBox.warning(self, "Error", "No data for PDF 1 to save!")
            return

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Excel for PDF 1", "", "Excel Files (*.xlsx)", options=options)
        
        if file_path:
            with pd.ExcelWriter(file_path) as writer:
                self.pdf1_tables.to_excel(writer, sheet_name='Tables', index=False)
            QMessageBox.information(self, "Saved", f"PDF 1 data saved to {file_path}")

    def save_csv_pdf2(self):
        if self.pdf2_tables.empty:
            QMessageBox.warning(self, "Error", "No data for PDF 2 to save!")
            return

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Excel for PDF 2", "", "Excel Files (*.xlsx)", options=options)
        
        if file_path:
            with pd.ExcelWriter(file_path) as writer:
                self.pdf2_tables.to_excel(writer, sheet_name='Tables', index=False)
            QMessageBox.information(self, "Saved", f"PDF 2 data saved to {file_path}")

# Main function to run the application
def main():
    app = QApplication(sys.argv)
    ex = EntityExtractorApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
