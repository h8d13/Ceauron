from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

def open_website(url):
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Use the system's chromedriver
    service = Service('/usr/bin/chromedriver')
    
    # Initialize the Chrome driver
    driver = webdriver.Chrome(
        service=service,
        options=chrome_options
    )
    
    # Open the website
    driver.get(url)
    
    # Keep the browser open
    input("Press Enter to close the browser...")
    
    # Close the browser
    driver.quit()

if __name__ == "__main__":
    website_url = "https://www.example.com"  # Replace with your desired URL
    open_website(website_url)