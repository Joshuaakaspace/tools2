import pandas as pd
import re

# Sample text input
text = """
Regulations Amending the Special Economic Measures (Belarus) Regulations
...
Amendments
1 Part 1 of Schedule 1 to the Special Economic Measures (Belarus) Regulations1 is amended by adding the following in numerical order:
123. Nikolai Aleksandrovich LUKASHENKO (born on August 31, 2004) (also known as Mikalay Alyaksandravich LUKASHENKA and Kolya LUKASHENKO)
456. Yuliya Aleksandrovna BLIZNIUK (born on September 23, 1971)
789. Vitali Viktorovich SINILO
...
2 Part 1.1 of Schedule 1 to the Regulations is amended by adding the following in numerical order:
...
"""

# Extracting all content under the "Amendments" section
amendments_text = re.search(r'Amendments(.*)', text, re.DOTALL)

data = []

if amendments_text:
    # Extracting records with optional birth and alias details
    records = re.findall(r'(\d+)\.\s([^\(]+)(?:\s\(born on\s([^)]+)\))?(?:\s\(also known as\s([^)]+)\))?', amendments_text.group(1))
    for record in records:
        data.append({
            "ID": record[0],
            "Name": record[1].strip(),
            "Date of Birth": record[2] if len(record) > 2 else "",
            "Also Known As": record[3] if len(record) > 3 else "",
            "Status": "ADDED"
        })
else:
    print("No amendments section found or no matching records.")

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel
df.to_excel("/mnt/data/AmendmentRecords_Optional.xlsx", index=False)

df
