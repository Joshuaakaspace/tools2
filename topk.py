import pdfplumber
import pandas as pd
from PyPDF2 import PdfReader
from urllib.parse import unquote

def extract_table_from_pdf(pdf_path, limit=10):
    print("Starting PDF processing...")
    tables = []
    hyperlinks = {}
    
    # Extract tables using pdfplumber
    print("Extracting tables...")
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                tables.extend(table)
                if len(tables) > limit:
                    break
            if len(tables) > limit:
                break
    
    print(f"Extracted {len(tables)} rows from tables.")

    # Extract hyperlinks using PyPDF2
    print("Extracting hyperlinks...")
    reader = PdfReader(pdf_path)
    for page_num, page in enumerate(reader.pages):
        if '/Annots' in page:
            for annot in page['/Annots']:
                obj = annot.get_object()
                if '/A' in obj and '/URI' in obj['/A']:
                    uri = obj['/A']['/URI']
                    if '/Rect' in obj:
                        x1, y1, x2, y2 = obj['/Rect']
                        hyperlinks[(page_num, x1, y1, x2, y2)] = unquote(uri)

    print(f"Extracted {len(hyperlinks)} hyperlinks.")

    # Convert to DataFrame
    print("Creating DataFrame...")
    df = pd.DataFrame(tables[1:limit+1], columns=tables[0])

    print(f"Created DataFrame with {len(df)} rows.")

    # Add hyperlink columns
    df['First_Column_Hyperlink'] = ''
    df['Last_Column_Hyperlink'] = ''

    # Match hyperlinks to table cells
    print("Matching hyperlinks to cells...")
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            words = page.extract_words(x_tolerance=3, y_tolerance=3, keep_blank_chars=True)
            for i, row in df.iterrows():
                print(f"Processing row {i+1}/{len(df)}...")
                first_cell = row.iloc[0]
                last_cell = row.iloc[-1]
                
                for word in words:
                    for (p, x1, y1, x2, y2), uri in hyperlinks.items():
                        if p == page_num and word['x0'] >= x1 and word['top'] >= y1 and word['x1'] <= x2 and word['bottom'] <= y2:
                            if word['text'] in first_cell:
                                df.at[i, 'First_Column_Hyperlink'] = uri
                            if word['text'] in last_cell:
                                df.at[i, 'Last_Column_Hyperlink'] = uri

    print("Processing complete.")
    return df

# Usage
pdf_path = 'path/to/your/pdf/file.pdf'
result_df = extract_table_from_pdf(pdf_path)
print("\nFinal DataFrame:")
print(result_df)

# Optionally, save to CSV
result_df.to_csv('extracted_data.csv', index=False)
print("\nData saved to 'extracted_data.csv'")