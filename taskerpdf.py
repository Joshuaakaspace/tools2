import pdfplumber
import pandas as pd
from PyPDF2 import PdfReader
from urllib.parse import unquote

def extract_sanctions_table(pdf_path, limit=10):
    print("Starting PDF processing...")
    tables = []
    hyperlinks = {}
    
    columns = ["Sanction Name", "Entity", "Location of Entity", "Date Imposed", "Status/Date of Expiration", "Federal Register Notice"]
    
    # Extract tables using pdfplumber
    print("Extracting tables...")
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_tables = page.extract_tables()
            for table in extracted_tables:
                if table and len(table[0]) == len(columns):  # Check if table matches expected columns
                    tables.extend(table)
                    if len(tables) > limit + 1:  # +1 for header
                        break
            if len(tables) > limit + 1:
                break
    
    print(f"Extracted {len(tables) - 1} rows from tables.")

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
    df = pd.DataFrame(tables[1:limit+1], columns=columns)

    print(f"Created DataFrame with {len(df)} rows.")

    # Add hyperlink columns
    df['Sanction_Name_Hyperlink'] = ''
    df['Federal_Register_Notice_Hyperlink'] = ''

    # Match hyperlinks to table cells
    print("Matching hyperlinks to cells...")
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            words = page.extract_words(x_tolerance=3, y_tolerance=3, keep_blank_chars=True)
            for i, row in df.iterrows():
                print(f"Processing row {i+1}/{len(df)}...")
                sanction_name = row['Sanction Name']
                federal_register = row['Federal Register Notice']
                
                for word in words:
                    for (p, x1, y1, x2, y2), uri in hyperlinks.items():
                        if p == page_num and word['x0'] >= x1 and word['top'] >= y1 and word['x1'] <= x2 and word['bottom'] <= y2:
                            if word['text'] in sanction_name:
                                df.at[i, 'Sanction_Name_Hyperlink'] = uri
                            if word['text'] in federal_register:
                                df.at[i, 'Federal_Register_Notice_Hyperlink'] = uri

    print("Processing complete.")
    return df

# Usage
pdf_path = 'path/to/your/sanctions_list.pdf'
result_df = extract_sanctions_table(pdf_path)
print("\nFinal DataFrame:")
print(result_df)

# Optionally, save to CSV
result_df.to_csv('extracted_sanctions_data.csv', index=False)
print("\nData saved to 'extracted_sanctions_data.csv'")