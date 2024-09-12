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
"""

# Extracting all content under the "Amendments" section
amendments_text = re.search(r'Amendments(.*)', text, re.DOTALL)

data = []

if amendments_text:
    # Extracting records with an 'or' structure in regex for optional parts
    records = re.findall(r'(\d+)\.\s([^\(]+?)(?:\s\(born on\s([^)]+)\))?(?:\s\(also known as\s([^)]+)\))?|\d+\.\s([^\(]+?)(?:\s\(born on\s([^)]+)\))|\d+\.\s([^\(]+)', amendments_text.group(1), re.MULTILINE)
    for record in records:
        # Normalize the record structure as regex groups vary
        id = record[0] if record[0] else (record[4] if record[4] else record[6])
        name = record[1].strip() if record[1] else (record[5].strip() if record[5] else record[7].strip())
        dob = record[2] if record[2] else (record[6] if record[6] else "")
        aka = record[3] if record[3] else ""
        data.append({
            "ID": id,
            "Name": name,
            "Date of Birth": dob,
            "Also Known As": aka,
            "Status": "ADDED"
        })
else:
    print("No amendments section found or no matching records.")

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel
df.to_excel("/mnt/data/AmendmentRecords_AllFormats.xlsx", index=False)

df
