from bs4 import BeautifulSoup
import re

# Example large HTML input (your full HTML page)
html = '''
<div id="content">
<h1 id="wb-cont">Regulations Amending the Special Economic Measures (Venezuela) Regulations:&nbsp;SOR/2019-263</h1>
<p>Canada Gazette, Part II, Volume 153, Number 14</p>
<p>Registration</p>
<p>SOR/2019-263&nbsp;June&nbsp;25,&nbsp;2019</p>
<p>SPECIAL ECONOMIC MEASURES ACT</p>
<p>P.C. 2019-953&nbsp;June&nbsp;22,&nbsp;2019</p>
<p>Her Excellency the Governor General in Council, on the recommendation of the Minister of Foreign Affairs, pursuant to subsections&nbsp;4(1)<sup id="footnoteRef.51489"> <a class="fn-lnk" href="#footnote.51489"><span class="wb-inv">footnote </span>a</a></sup>, (1.1)<sup id="nbfn1"><a class="fn-lnk" href="#footnote.51489"><span class="wb-inv">footnote </span>a</a></sup>, (2) and (3) of the <cite>Special Economic Measures Act</cite><sup id="footnoteRef.51491"> <a class="fn-lnk" href="#footnote.51491"><span class="wb-inv">footnote </span>b</a></sup>, makes the annexed <cite>Regulations Amending the Special Economic Measures (Venezuela) Regulations</cite>.</p>
<h2>Regulations Amending the Special Economic Measures (Venezuela) Regulations</h2>
<h3>Amendment</h3>
<p><strong>1 Item 57 of the Schedule to the <cite>Special Economic Measures (Venezuela) Regulations</cite></strong><sup id="footnoteRef.51492"> <a class="fn-lnk" href="#footnote.51492"><span class="wb-inv">footnote </span>1</a></sup><strong> is repealed.</strong></p>
<h3>Application Prior to Publication</h3>
<p><strong>2 For the purpose of paragraph&nbsp;11(2)(a) of the <cite>Statutory Instruments Act</cite>, these Regulations apply before they are published in the <cite>Canada Gazette</cite>.</strong></p>
<h3>Coming into Force</h3>
<p><strong>3 These Regulations come into force on the day on which they are registered.</strong></p>
...
</div>
'''

# Step 1: Parse the HTML and search for the 'Item' and 'Part' values
def extract_item_part_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find all <p> tags and check if they contain 'Item' and 'repealed'
    for p_tag in soup.find_all('p'):
        text = p_tag.get_text()
        if 'Item' in text and 'repealed' in text:
            print(f"Found matching <p> tag: {text}")  # Debug statement
            
            # Extract the Item number using regular expressions
            item_match = re.search(r'Item\s+(\d+)', text)
            part_match = re.search(r'Part\s+(\d+)', text)

            item_number = int(item_match.group(1)) if item_match else None
            part_number = int(part_match.group(1)) if part_match else None

            print(f"Extracted Item: {item_number}, Part: {part_number}")  # Debug statement
            return item_number, part_number
    
    print("No matching <p> tag with 'Item' and 'repealed' found.")  # Debug statement
    return None, None

# Extract item and part from the HTML
item_number, part_number = extract_item_part_from_html(html)

# Output the extracted Item and Part numbers
item_number, part_number
