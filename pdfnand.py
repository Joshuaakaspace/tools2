import PyPDF2
import pandas as pd
import tabula

def extract_pdf_info(pdf_path):
    # Extract text and hyperlinks
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)
        
        text_content = []
        hyperlinks = []
        
        for page_num in range(num_pages):
            page = reader.pages[page_num]
            
            # Extract text
            text = page.extract_text()
            text_content.append(text)
            
            # Extract hyperlinks
            if '/Annots' in page:
                for annot in page['/Annots']:
                    obj = annot.get_object()
                    if obj.get('/Subtype') == '/Link':
                        if '/A' in obj and '/URI' in obj['/A']:
                            uri = obj['/A']['/URI']
                            hyperlinks.append(uri)
    
    # Extract tables
    tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
    
    # Combine all tables into a single DataFrame
    if tables:
        combined_df = pd.concat(tables, ignore_index=True)
    else:
        combined_df = pd.DataFrame()
    
    # Create a DataFrame for text and hyperlinks
    text_df = pd.DataFrame({'Page': range(1, num_pages + 1), 'Text': text_content})
    hyperlinks_df = pd.DataFrame({'Hyperlinks': hyperlinks})
    
    return combined_df, text_df, hyperlinks_df

# Example usage
pdf_path = 'path/to/your/pdf/file.pdf'
table_df, text_df, hyperlinks_df = extract_pdf_info(pdf_path)

print("Table Data:")
print(table_df)

print("\nText Data:")
print(text_df)

print("\nHyperlinks Data:")
print(hyperlinks_df)