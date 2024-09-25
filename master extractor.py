from bs4 import BeautifulSoup

# Sample HTML content
html_content = '''<div class="Schedule" id="1261281"><header><h2 class="scheduleLabel" id="h-1261282"><span class="scheduleLabel">SCHEDULE 1</span><span class="OriginatingRef">(Section 2 and subsections 8(1) and (2))</span><span class="scheduleTitleText">
Persons</span><br></h2></header><figure><figcaption><p><span class="HLabel">PART 1</span></p><p><span class="HTitleText1">Individuals — Gross Human Rights Violations</span></p>SOR/2022-49, s. 5</figcaption><ul class="noBullet"><li><div class="listItemBlock0"><div class="listItemLabel"><span class="lawlabel">1</span>&nbsp;</div><div class="listItemText2">Khazalbek Bakhtibekovich Atabekov</div></div></li><li><div class="listItemBlock0"><div class="listItemLabel"><span class="lawlabel">2</span>&nbsp;</div><div class="listItemText2">Dmitry Vladimirovich Balaba</div></div></li><li><div class="listItemBlock0"><div class="listItemLabel"><span class="lawlabel">3</span>&nbsp;</div><div class="listItemText2">Aleksandr Petrovich Barsukov</div></div></li><li><div class="listItemBlock0"><div class="listItemLabel"><span class="lawlabel">4</span>&nbsp;</div><div class="listItemText2">Yelena Nikolaevna Dmukhailo</div></div></li><li><div class="listItemBlock0"><div class="listItemLabel"><span class="lawlabel">5</span>&nbsp;</div><div class="listItemText2">Vadim Dmitriyevich Ipatov</div></div></li> <!-- more items --> </ul></div>'''

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Extract all the names of individuals from <div class="listItemText2"> tags
names = [item.get_text() for item in soup.find_all('div', class_='listItemText2')]

# Print the extracted names
for name in names:
    print(name)
