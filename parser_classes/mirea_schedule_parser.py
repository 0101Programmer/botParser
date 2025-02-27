import time
from PIL import Image

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from pathlib import Path

# Путь к папке
folder_path = Path("../media/mirea_schedule_parser_media")

# Проверка, существует ли папка
if folder_path.exists() and folder_path.is_dir():
    print("Папка существует.")
else:
    print("Папка не существует.")

options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Включаем headless-режим
options.add_argument("--disable-gpu")  # Отключаем GPU (рекомендуется для headless)

# Создаем объект браузера (в данном случае Chrome)
driver = webdriver.Chrome(options=options)

# Открываем страницу
driver.get("https://www.mirea.ru/schedule/")
original_size = driver.get_window_size()

# Находим iframe (например, по ID)
iframe = driver.find_element(By.ID, 'schedule_iframe')


location = iframe.location
print(location)


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
driver.save_screenshot("screenshot.png")
driver.set_window_size(original_size['width'], original_size['height'])

# ---

# Загружаем скриншот с помощью Pillow
screenshot = Image.open("screenshot.png")

# Координаты области, которую нужно вырезать
left = 40    # x-координата
top = 773    # y-координата
width = 500  # ширина области (укажите нужное значение)
height = 750 # высота области (укажите нужное значение)

# Вычисляем правую и нижнюю границы
right = left + width + 80
bottom = top + height + 150

# Обрезаем скриншот до нужной области
cropped_screenshot = screenshot.crop((left, top, right, bottom))

# Сохраняем обрезанный скриншот
cropped_screenshot.save("../media/mirea_schedule_parser_media/cropped_screenshot.png")


# Завершаем работу
driver.quit()