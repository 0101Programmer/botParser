import logging
import time
from pathlib import Path

from PIL import Image
import uuid

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver import ActionChains
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

    def datetime_now_schedule_page_parser(self, group_number: str, path_to_mirea_schedule_parser_media="../media/mirea_schedule_parser_media/"):
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

                # Ожидаем, чтобы прогрузить результат на странице ("some-plug-class" - просто заглушка)
                try:
                    WebDriverWait(self.driver, 5).until(
                        ec.presence_of_element_located((By.CLASS_NAME, "some-plug-class"))
                    )
                    logging.info("'some-plug-class' was found")
                except TimeoutException as e:
                    logging.info(f"No any 'some-plug-class' was found: {e}")

                self.driver.save_screenshot('test.png')

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

    def particular_date_schedule_parser(self, group_number: str, path_to_schedule_parser_media="../media/schedule_parser_media/"):
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
                # Теперь ищем элемент (class="SelectDateButtons_buttons___VT0o") внутри iframe
                select_date_buttons = WebDriverWait(self.driver, 10).until(
                    ec.presence_of_element_located((By.CLASS_NAME, "SelectDateButtons_buttons___VT0o"))
                )

                # Находим кнопку с классами "rs-btn rs-btn-default"
                middle_button = select_date_buttons.find_element(
                    By.XPATH,
                    ".//button[contains(@class, 'rs-btn') "
                    "and contains(@class, 'rs-btn-default') "
                    "and not(contains(@class, 'rs-btn-icon'))]"
                )
                middle_button.click()

                # Ожидаем появления нового элемента (class="SelectDateButtons_body__2bD_P")
                select_date_buttons_body = WebDriverWait(self.driver, 10).until(
                    ec.presence_of_element_located((By.CLASS_NAME, "SelectDateButtons_body__2bD_P"))
                )
                print(select_date_buttons_body.get_attribute('innerHTML'))

                # Находим кнопку "Previous month"
                previous_month_button = select_date_buttons_body.find_element(
                    By.XPATH, ".//button[@aria-label='Previous month']"
                )

                # Выполняем клик через JavaScript (если обычный клик не работает)
                self.driver.execute_script("arguments[0].click();", previous_month_button)
                print("Кнопка 'Previous month' нажата через JavaScript.")

                # Ожидаем, чтобы прогрузить результат на странице ("some-plug-class" - просто заглушка)
                try:
                    WebDriverWait(self.driver, 5).until(
                        ec.presence_of_element_located((By.CLASS_NAME, "some-plug-class"))
                    )
                    logging.info("'some-plug-class' was found")
                except TimeoutException as e:
                    logging.info(f"No any 'some-plug-class' was found: {e}")

                self.driver.save_screenshot('test.png')

            except TimeoutException as e:
                logging.info(f"Элемент по CLASS_NAME 'rs-btn rs-btn-default' не найден: {e}")

        except TimeoutException as e:
            logging.info(f"Элемент по ID 'schedule_iframe' не найден: {e}")
        finally:

            # Возвращаемся на основную страницу
            # self.driver.switch_to.default_content()

            self.driver.quit()


# test_class = MireaScheduleParser()
# #
# # print(test_class.datetime_now_schedule_page_parser("УДМО-01-24"))
# test_class.particular_date_schedule_parser("УДМО-01-24")