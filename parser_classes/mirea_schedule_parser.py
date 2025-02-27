import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Включаем headless-режим
options.add_argument("--disable-gpu")  # Отключаем GPU (рекомендуется для headless)

# Создаем объект браузера (в данном случае Chrome)
driver = webdriver.Chrome(options=options)

# Открываем страницу
driver.get("https://www.mirea.ru/schedule/")
original_size = driver.get_window_size()

# Ждём загрузки страницы
# time.sleep(3)

# Находим iframe (например, по ID)
iframe = driver.find_element(By.ID, 'schedule_iframe')

# Переключаемся на iframe
driver.switch_to.frame(iframe)

# Теперь ищем элемент внутри iframe
element = driver.find_element(By.ID, 'rs-:Rlhr6:')


# Выводим информацию об элементе
# print("Текст элемента:", element.text)
# print("ID элемента:", element.get_attribute('id'))
# print("Класс элемента:", element.get_attribute('class'))
# print("HTML-код элемента:", element.get_attribute('outerHTML'))

element.send_keys('УДМО-01-24')

# Ждём, чтобы увидеть результат
time.sleep(3)

element.send_keys(Keys.ARROW_DOWN)  # Navigate down to the desired suggestion
element.send_keys(Keys.ENTER)

time.sleep(3)


# Делаем скриншот, чтобы сохранить результат
# driver.save_screenshot('screenshot.png')

# (Опционально) Возвращаемся на основную страницу
driver.switch_to.default_content()

required_width = driver.execute_script('return document.body.parentNode.scrollWidth')
required_height = driver.execute_script('return document.body.parentNode.scrollHeight')
driver.set_window_size(required_width, required_height)
driver.save_screenshot("screenshot.png")  # has scrollbar
driver.set_window_size(original_size['width'], original_size['height'])

# ---

# Завершаем работу
driver.quit()