import sys
import pdfplumber
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox
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
        for page in pdf.pages:
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
        layout = QVBoxLayout()

        # Label for instruction
        self.label = QLabel("Select two PDF files and compare data based on 'Name', 'NAME', 'Nama', 'name':")
        layout.addWidget(self.label)

        # Button to load PDF 1 for text extraction
        self.load_pdf1_btn = QPushButton("Load PDF 1", self)
        self.load_pdf1_btn.clicked.connect(self.load_pdf1)
        layout.addWidget(self.load_pdf1_btn)

        # Button to load PDF 2 for text extraction
        self.load_pdf2_btn = QPushButton("Load PDF 2", self)
        self.load_pdf2_btn.clicked.connect(self.load_pdf2)
        layout.addWidget(self.load_pdf2_btn)

        # Button to compare the two PDFs for text
        self.compare_btn = QPushButton("Compare Texts and Save Delta", self)
        self.compare_btn.setEnabled(False)  # Disable until both PDFs are loaded
        self.compare_btn.clicked.connect(self.compare_pdfs)
        layout.addWidget(self.compare_btn)

        # Button to extract tables from PDF 1
        self.extract_table_pdf1_btn = QPushButton("Extract Tables from PDF 1", self)
        self.extract_table_pdf1_btn.clicked.connect(self.extract_table_pdf1)
        layout.addWidget(self.extract_table_pdf1_btn)

        # Button to extract tables from PDF 2
        self.extract_table_pdf2_btn = QPushButton("Extract Tables from PDF 2", self)
        self.extract_table_pdf2_btn.clicked.connect(self.extract_table_pdf2)
        layout.addWidget(self.extract_table_pdf2_btn)

        # Button to compare tables and save delta
        self.compare_tables_btn = QPushButton("Compare Tables and Save Delta", self)
        self.compare_tables_btn.setEnabled(False)  # Disable until both PDFs are loaded
        self.compare_tables_btn.clicked.connect(self.compare_tables)
        layout.addWidget(self.compare_tables_btn)

        # Button to save CSV for PDF 1 (text and tables)
        self.save_csv_pdf1_btn = QPushButton("Save CSV for PDF 1", self)
        self.save_csv_pdf1_btn.setEnabled(False)  # Disable until PDF 1 is loaded
        self.save_csv_pdf1_btn.clicked.connect(self.save_csv_pdf1)
        layout.addWidget(self.save_csv_pdf1_btn)

        # Button to save CSV for PDF 2 (text and tables)
        self.save_csv_pdf2_btn = QPushButton("Save CSV for PDF 2", self)
        self.save_csv_pdf2_btn.setEnabled(False)  # Disable until PDF 2 is loaded
        self.save_csv_pdf2_btn.clicked.connect(self.save_csv_pdf2)
        layout.addWidget(self.save_csv_pdf2_btn)

        # Set the layout for the main window
        self.setLayout(layout)
        self.setWindowTitle("PDF Comparison Tool")
        self.setGeometry(300, 300, 400, 250)

    def load_pdf1(self):
        # Open file dialog to select PDF 1
        options = QFileDialog.Options()
        pdf_path, _ = QFileDialog.getOpenFileName(self, "Open PDF 1", "", "PDF Files (*.pdf)", options=options)
        
        if pdf_path:
            # Extract and process the data for PDF 1
            text = extract_text_from_pdf(pdf_path)
            if not text:
                QMessageBox.critical(self, "Error", "Failed to extract text from PDF 1.")
                return

            self.pdf1_data = extract_details_by_keyword(text)
            self.pdf1_tables = extract_tables_from_pdf(pdf_path)
            if not self.pdf1_data and self.pdf1_tables.empty:
                QMessageBox.information(self, "No Data", "No entities or tables found in PDF 1.")
            else:
                QMessageBox.information(self, "Success", "PDF 1 data loaded successfully.")
                self.save_csv_pdf1_btn.setEnabled(True)  # Enable the button to save CSV for PDF 1
                if self.pdf2_data or not self.pdf2_tables.empty:
                    self.compare_btn.setEnabled(True)  # Enable compare button if both PDFs are loaded

    def load_pdf2(self):
        # Open file dialog to select PDF 2
        options = QFileDialog.Options()
        pdf_path, _ = QFileDialog.getOpenFileName(self, "Open PDF 2", "", "PDF Files (*.pdf)", options=options)
        
        if pdf_path:
            # Extract and process the data for PDF 2
            text = extract_text_from_pdf(pdf_path)
            if not text:
                QMessageBox.critical(self, "Error", "Failed to extract text from PDF 2.")
                return

            self.pdf2_data = extract_details_by_keyword(text)
            self.pdf2_tables = extract_tables_from_pdf(pdf_path)
            if not self.pdf2_data and self.pdf2_tables.empty:
                QMessageBox.information(self, "No Data", "No entities or tables found in PDF 2.")
            else:
                QMessageBox.information(self, "Success", "PDF 2 data loaded successfully.")
                self.save_csv_pdf2_btn.setEnabled(True)  # Enable the button to save CSV for PDF 2
                if self.pdf1_data or not self.pdf1_tables.empty:
                    self.compare_btn.setEnabled(True)  # Enable compare button if both PDFs are loaded

    def compare_tables(self):
        if self.pdf1_tables.empty or self.pdf2_tables.empty:
            QMessageBox.warning(self, "Error", "Please extract tables from both PDFs before comparing.")
            return

        # Perform comparison using DeepDiff to find differences
        delta = DeepDiff(self.pdf1_tables.to_dict(), self.pdf2_tables.to_dict(), ignore_order=True).to_dict()

        if not delta:
            QMessageBox.information(self, "No Difference", "The two PDFs have no table differences.")
        else:
            # Save the delta (difference) file
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Table Delta Excel", "", "Excel Files (*.xlsx)", options=options)

            if file_path:
                df_delta = pd.DataFrame([delta])
                df_delta.to_excel(file_path, index=False)
                QMessageBox.information(self, "Saved", f"Table delta file saved to {file_path}")

    def save_csv_pdf1(self):
        # Save the processed data (text and tables) for PDF 1 to a CSV file
        if not self.pdf1_data and self.pdf1_tables.empty:
            QMessageBox.warning(self, "Error", "No data for PDF 1 to save!")
            return
        
        # Open file dialog to save the file
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Excel for PDF 1", "", "Excel Files (*.xlsx)", options=options)
        
        if file_path:
            with pd.ExcelWriter(file_path) as writer:
                if self.pdf1_data:
                    df_text = pd.DataFrame(self.pdf1_data)
                    df_text.to_excel(writer, sheet_name='Text', index=False)
                if not self.pdf1_tables.empty:
                    self.pdf1_tables.to_excel(writer, sheet_name='Tables', index=False)
            QMessageBox.information(self, "Saved", f"PDF 1 data (text and tables) saved to {file_path}")

    def save_csv_pdf2(self):
        # Save the processed data (text and tables) for PDF 2 to a CSV file
        if not self.pdf2_data and self.pdf2_tables.empty:
            QMessageBox.warning(self, "Error", "No data for PDF 2 to save!")
            return
        
        # Open file dialog to save the file
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Excel for PDF 2", "", "Excel Files (*.xlsx)", options=options)
        
        if file_path:
            with pd.ExcelWriter(file_path) as writer:
                if self.pdf2_data:
                    df_text = pd.DataFrame(self.pdf2_data)
                    df_text.to_excel(writer, sheet_name='Text', index=False)
                if not self.pdf2_tables.empty:
                    self.pdf2_tables.to_excel(writer, sheet_name='Tables', index=False)
            QMessageBox.information(self, "Saved", f"PDF 2 data (text and tables) saved to {file_path}")

# Main function to run the application
def main():
    app = QApplication(sys.argv)
    ex = EntityExtractorApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
