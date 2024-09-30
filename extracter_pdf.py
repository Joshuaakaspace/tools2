import pdfplumber
import pandas as pd
from urllib.parse import unquote

def extract_table_from_pdf(pdf_path):
    tables = []
    hyperlinks = {}
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Extract tables
            for table in page.extract_tables():
                tables.extend(table)
            
            # Extract hyperlinks
            for annot in page.hyperlinks:
                if annot['uri']:
                    key = (annot['x0'], annot['top'], annot['x1'], annot['bottom'])
                    hyperlinks[key] = unquote(annot['uri'])

    # Convert to DataFrame
    df = pd.DataFrame(tables[1:], columns=tables[0])

    # Add hyperlink columns
    df['First_Column_Hyperlink'] = ''
    df['Last_Column_Hyperlink'] = ''

    for i, row in df.iterrows():
        for char in page.chars:
            char_key = (char['x0'], char['top'], char['x1'], char['bottom'])
            if char_key in hyperlinks:
                if char['x0'] == df.iloc[i, 0]['x0']:  # First column
                    df.at[i, 'First_Column_Hyperlink'] = hyperlinks[char_key]
                elif char['x1'] == df.iloc[i, -1]['x1']:  # Last column
                    df.at[i, 'Last_Column_Hyperlink'] = hyperlinks[char_key]

    return df

# Usage
pdf_path = 'path/to/your/pdf/file.pdf'
result_df = extract_table_from_pdf(pdf_path)
print(result_df)

# Optionally, save to CSV
result_df.to_csv('extracted_data.csv', index=False)