from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Set up the WebDriver
driver = webdriver.Chrome()

# Open Google
driver.get("http://localhost:3000")
driver.maximize_window()

# Usuário
element = driver.find_element(By.NAME, "user")
element.send_keys("admin")

element = driver.find_element(By.NAME, "password")
element.send_keys("123")

# Simulate pressing the Enter key
element.send_keys(Keys.RETURN)

# Wait for a few seconds to see the results
time.sleep(5)

element = driver.find_element(By.XPATH,"/html/body/div/div[1]/div/ul/a[2]/ul/li/li/div")
element.click()

element = driver.find_element(By.XPATH, "/html/body/div/div[1]/div/ul/a[2]/ul/div/ul/a[1]/a/li/div")
element.click()

element = driver.find_element(By.XPATH,"/html/body/div/div[2]/div[1]/div/div/div/div[2]/div[1]/div[2]/a/div/button")
element.click()

time.sleep(5)


# Inicia preenchimento
element = driver.find_element(By.NAME, "nome")
element.send_keys("teste")

element = driver.find_element(By.NAME, "nome_social")
element.send_keys("teste")

element = driver.find_element(By.NAME, "data_nascimento")
element.send_keys(11012024)

time.sleep(5)

# Close the browser
driver.quit()