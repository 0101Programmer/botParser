import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Включаем headless-режим
options.add_argument("--disable-gpu")  # Отключаем GPU (рекомендуется для headless)

# Создаем объект браузера (в данном случае Chrome)
driver = webdriver.Chrome(options=options)

# Открываем страницу
driver.get("https://www.mirea.ru/schedule/")

# ---

# Ждём загрузки страницы
# time.sleep(3)

# Находим iframe (например, по ID)
iframe = driver.find_element(By.ID, 'schedule_iframe')  # Замените 'iframe-id' на реальный ID

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
# time.sleep(3)

# Делаем скриншот, чтобы сохранить результат
driver.save_screenshot('screenshot.png')

# (Опционально) Возвращаемся на основную страницу
driver.switch_to.default_content()

# ---



# Завершаем работу
driver.quit()