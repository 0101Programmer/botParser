import logging
import time
from pathlib import Path

from PIL import Image
import uuid

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

# Настройка логгирования
logging.basicConfig(level=logging.INFO)

class MireaScheduleParser:
    def __init__(self):
        # url сайта
        self.mirea_schedule_url = "https://www.mirea.ru/schedule/"
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--headless")  # Включаем headless-режим
        self.options.add_argument("--disable-gpu")  # Отключаем GPU (рекомендуется для headless)
        # Создаем объект браузера (в данном случае Chrome)
        self.driver = webdriver.Chrome(options=self.options)
        # заготовка для получения координат рамки с расписанием
        self.schedule_box_location = ''
        # имя финального скриншота с расписанием, для того, чтобы передать его
        # через бота, а потом удалить из файлов
        self.cropped_screenshot_name = ''

    def page_parser(self, group_number: str, path_to_mirea_schedule_parser_media="../media/mirea_schedule_parser_media/"):
        # Открываем страницу
        self.driver.get("https://www.mirea.ru/schedule/")
        # Сохраняем её размер (чтобы потом сделать скриншот)
        original_size = self.driver.get_window_size()

        # Находим iframe с расписанием (+ ждём загрузку)
        try:
            iframe = WebDriverWait(self.driver, 10).until(
                ec.presence_of_element_located((By.ID, "schedule_iframe")))
            # получаем его координаты, чтобы потом обрезать скриншот всей страницы по ним
            schedule_box_location = iframe.location
            self.schedule_box_location = schedule_box_location
            # Переключаемся на iframe
            self.driver.switch_to.frame(iframe)
            try:
                # Теперь ищем элемент внутри iframe
                element = WebDriverWait(self.driver, 10).until(
                    ec.presence_of_element_located((By.ID, "rs-:Rlhr6:")))
                # отправляем значение номера группы в поле для ввода
                element.send_keys(str(group_number))
                # Ждём загрузки подсказки для выбора номера группы
                self.driver.implicitly_wait(5)
                # выбираем предложенный вариант из списка
                element.send_keys(Keys.ARROW_DOWN)
                element.send_keys(Keys.ENTER)
                # Ждём, чтобы увидеть результат
                self.driver.implicitly_wait(5)

            except TimeoutException as e:
                logging.info(f"Элемент по ID 'rs-:Rlhr6:' не найден: {e}")

        except TimeoutException as e:
            logging.info(f"Элемент по ID 'schedule_iframe' не найден: {e}")
        finally:

            # Возвращаемся на основную страницу
            self.driver.switch_to.default_content()

            # делаем скриншот страницы (по размеру страницы)
            required_width = self.driver.execute_script('return document.body.parentNode.scrollWidth')
            required_height = self.driver.execute_script('return document.body.parentNode.scrollHeight')
            self.driver.set_window_size(required_width, required_height)
            unique_screenshot_id = uuid.uuid4()
            screenshot_name = f'{unique_screenshot_id}_{group_number}_screenshot.png'
            self.driver.save_screenshot(f"{path_to_mirea_schedule_parser_media}{screenshot_name}")
            self.driver.set_window_size(original_size['width'], original_size['height'])

            # Загружаем скриншот с помощью Pillow
            screenshot = Image.open(f"{path_to_mirea_schedule_parser_media}{screenshot_name}")

            # Координаты области, которую нужно вырезать
            left = self.schedule_box_location['x']  # x-координата
            top = self.schedule_box_location['y']  # y-координата
            width = 500  # ширина области
            height = 750  # высота области

            # Вычисляем правую и нижнюю границы
            right = left + width + 80
            bottom = top + height + 150

            # Обрезаем скриншот до нужной области
            cropped_screenshot = screenshot.crop((left, top, right, bottom))

            # Сохраняем обрезанный скриншот
            cropped_screenshot_name = f"cropped_{screenshot_name}"
            cropped_screenshot.save(f"{path_to_mirea_schedule_parser_media}{cropped_screenshot_name}")
            self.cropped_screenshot_name = cropped_screenshot_name

            # удаляем исходный скриншот
            screenshot_name_path = Path(f"{path_to_mirea_schedule_parser_media}{screenshot_name}")
            try:
                # Удаление файла
                screenshot_name_path.unlink()
                logging.info(f"Скриншот '{screenshot_name}' удален.")
            except FileNotFoundError:
                logging.info(f"Скриншот '{screenshot_name}' не существует.")
            except Exception as e:
                logging.info(f"Ошибка при удалении скриншота '{screenshot_name}': {e}")

            self.driver.quit()
            return self.cropped_screenshot_name

# test_class = MireaScheduleParser()
#
# print(test_class.page_parser("УДМО-01-24"))