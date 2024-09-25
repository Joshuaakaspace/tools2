from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Setup Chrome webdriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

try:
    # Navigate to the specified URL
    driver.get("https://gazette.gc.ca/rp-pr/p2/2024/2024-08-28/html/sor-dors167-eng.html")

    # Locate the <li> element containing the specific link for 'Special Economic Measures (Belarus) Regulations'
    target_li = driver.find_element(By.XPATH, "//li[.//a[contains(text(), 'Special Economic Measures (Belarus) Regulations') and not(contains(text(), 'Amending'))]]")

    # Find the next sibling <li> element that contains the specific text 'Regulations Amending the Special Economic Measures'
    next_link_li = target_li.find_element(By.XPATH, './following-sibling::li[.//a[contains(text(), "Regulations Amending the Special Economic Measures")]]')

    # Find the <a> element within that sibling <li> and extract the href attribute
    link_element = next_link_li.find_element(By.TAG_NAME, 'a')
    link_url = link_element.get_attribute('href')
    print("URL found:", link_url)

finally:
    # Close the browser window
    driver.quit()
