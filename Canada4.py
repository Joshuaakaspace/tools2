from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Setup Chrome webdriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

try:
    # Navigate to the specified URL
    driver.get("https://gazette.gc.ca/rp-pr/p2/2024/2024-08-28/html/sor-dors167-eng.html")

    # Locate the 'Justice Canada consolidation of the Special Economic Measures (Belarus) Regulations' list item
    regulations_link = driver.find_element(By.XPATH, "//ul[@class='lst-spcd']//a[contains(text(), 'Special Economic Measures (Belarus) Regulations')]/../..")

    # Get the following list item
    next_li = regulations_link.find_element(By.XPATH, './following-sibling::li[1]')
    
    # Find the link within that list item
    link_element = next_li.find_element(By.TAG_NAME, 'a')

    # Get the href attribute to retrieve the URL
    link_url = link_element.get_attribute('href')
    print("URL found:", link_url)
finally:
    # Close the browser window
    driver.quit()
