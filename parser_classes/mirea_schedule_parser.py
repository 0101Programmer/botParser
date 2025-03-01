import datetime
import logging
import uuid
from pathlib import Path

from PIL import Image
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

# Настройка логирования
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
                # Теперь ищем элемент для ввода номера группы внутри iframe
                element = WebDriverWait(self.driver, 10).until(
                    ec.presence_of_element_located((By.ID, "rs-:Rlhr6:")))
                # отправляем значение номера группы в поле для ввода
                element.send_keys(str(group_number))
                # Ждём загрузки подсказки для выбора номера группы
                try:
                    WebDriverWait(self.driver, 5).until(
                        ec.presence_of_element_located((By.CLASS_NAME, "some-plug-class"))
                    )
                    logging.info("Suddenly 'some-plug-class' was found")
                except TimeoutException:
                    logging.info(f"Successful await")
                # выбираем предложенный вариант из списка
                element.send_keys(Keys.ARROW_DOWN)
                element.send_keys(Keys.ENTER)

                # Ожидаем, чтобы прогрузить результат на странице ("some-plug-class" - просто заглушка)
                try:
                    WebDriverWait(self.driver, 5).until(
                        ec.presence_of_element_located((By.CLASS_NAME, "some-plug-class"))
                    )
                    logging.info("Suddenly 'some-plug-class' was found")
                except TimeoutException:
                    logging.info(f"Successful await")

            except TimeoutException as e:
                logging.info(f"Элемент по ID 'rs-:Rlhr6:' не найден: {e}")

        except TimeoutException as e:
            logging.info(f"Элемент по ID 'schedule_iframe' не найден: {e}")
        finally:

            # Возвращаемся на основную страницу (фрейм)
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

    def particular_date_schedule_parser(self, group_number: str,
                                        path_to_mirea_schedule_parser_media="../media/mirea_schedule_parser_media/",
                                        previous_month=False, next_month=False, required_date=None
                                        ):
        """

        :param path_to_mirea_schedule_parser_media: путь для сохранения скриншота с расписанием
        :param required_date: дата, которую необходимо найти в формате "Январь, 2025, 5"
        :param group_number: номер группы
        :param previous_month: нужно ли искать данные за предыдущий месяц
        :param next_month: нужно ли искать данные за следующий месяц
        :return: название итогового скриншота с расписанием на конкретный день
        """

        # Словарь для преобразования русского названия месяца в числовое значение
        month_translation = {
            "Январь": 1,
            "Февраль": 2,
            "Март": 3,
            "Апрель": 4,
            "Май": 5,
            "Июнь": 6,
            "Июль": 7,
            "Август": 8,
            "Сентябрь": 9,
            "Октябрь": 10,
            "Ноябрь": 11,
            "Декабрь": 12,
        }

        # Преобразуем месяц в число
        month = month_translation[required_date.replace(' ', '').split(',')[0]]

        # Преобразуем год в число
        year = int(required_date.replace(' ', '').split(',')[1])

        # Преобразуем день в число
        day = int(required_date.replace(' ', '').split(',')[2])

        # Создаём объект datetime.date (день по умолчанию 1)
        parsed_required_date = datetime.date(year, month, day)

        # смотрим, за какой период (предыдущий, текущий, будущий) необходимо найти данные

        current_date = datetime.date.today()
        if (parsed_required_date.year, parsed_required_date.month) < (current_date.year, current_date.month):
            previous_month = True
        elif (parsed_required_date.year, parsed_required_date.month) > (current_date.year, current_date.month):
            next_month = True


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

                # Находим кнопку с классами "rs-btn rs-btn-default", при нажатии на которую появляется возможность
                # выбрать дату расписания (находится в центре)
                middle_calendar_header_button = select_date_buttons.find_element(
                    By.XPATH,
                    ".//button[contains(@class, 'rs-btn') "
                    "and contains(@class, 'rs-btn-default') "
                    "and not(contains(@class, 'rs-btn-icon'))]"
                )
                middle_calendar_header_button.click()

                # Ожидаем появления нового элемента (class="SelectDateButtons_body__2bD_P") - календарь для выбора даты
                select_date_buttons_body = WebDriverWait(self.driver, 10).until(
                    ec.presence_of_element_located((By.CLASS_NAME, "SelectDateButtons_body__2bD_P"))
                )

                # Находим кнопку "Select month", которая содержит текущий месяц и год
                # это будет необходимо, чтобы найти дату, указанную пользователем
                select_month_button = select_date_buttons_body.find_element(
                    By.XPATH, ".//button[@aria-label='Select month']"
                )

                # сохраняем координаты, в последствии по ним вычислим область клика, чтобы закрыть календарь
                select_month_button_location = select_month_button.location

                if previous_month:
                    # Находим кнопку "Previous month", будем нажимать на неё для прокрутки дат по месяцам
                    previous_month_button = select_date_buttons_body.find_element(
                        By.XPATH, ".//button[@aria-label='Previous month']"
                    )

                    # Выполняем клик через JavaScript (обычный клик тут не работает)

                    while not required_date.replace(' ', '').split(',')[0].lower().startswith(select_month_button.text.replace('.', '').split(',')[0]):
                        '''
                        Пока месяц запрошенной даты не начинается с первого значения кнопки select_month_button.text.replace('.', '').split(',')[0] (например, 'мар' - март)
                        цикл будет нажимать на кнопку перемотки даты
                        '''
                        self.driver.execute_script("arguments[0].click();", previous_month_button)

                elif next_month:
                    # Находим кнопку "Next month", здесь выполняется всё то же самое, но для поиска даты в будущем
                    next_month_button = select_date_buttons_body.find_element(
                        By.XPATH, ".//button[@aria-label='Next month']"
                    )

                    # Выполняем клик через JavaScript
                    while not required_date.replace(' ', '').split(',')[0].lower().startswith(
                            select_month_button.text.replace('.', '').split(',')[0]):
                        self.driver.execute_script("arguments[0].click();", next_month_button)

                # Ожидаем появления элемента (class="rs-calendar-body"), из него необходимо будет выбрать строку с неделей,
                # которая подходит под условие: запрашиваемый день и месяц

                calendar_body = WebDriverWait(self.driver, 10).until(
                    ec.presence_of_element_located((By.CLASS_NAME, "rs-calendar-body"))
                )

                # Находим все строки с ячейками
                rows = calendar_body.find_elements(By.XPATH,
                                                   ".//div[@role='row' and contains(@class, 'rs-calendar-table-row') and .//div[@role='gridcell']]")
                # Перебираем строки
                for row in rows:

                    # Находим и перебираем все ячейки в текущей строке (row)
                    cells = row.find_elements(By.CSS_SELECTOR, "div[role='gridcell']")
                    for cell in cells:
                        '''
                        Преобразуем атрибут 'aria-label' в такой вид, например, ['30', 'дек', '2024'], а далее проверяем,
                        совпадает ли значение какой-либо ячейки с запрошенными месяцем и числом и, если есть совпадение -
                        нажимаем на эту ячейку для выбора
                        '''
                        if (required_date.replace(' ', '').split(',')[0].lower().startswith(
                                cell.get_attribute('aria-label').replace('.', '').split()[1]) and
                                int(required_date.replace(' ', '').split(',')[2]) == int(cell.get_attribute(
                                    'aria-label').replace('.', '').split()[0])):
                            self.driver.execute_script("arguments[0].click();", cell)

                # Ожидаем, чтобы прогрузить результат на странице ("some-plug-class" - просто заглушка)
                try:
                    WebDriverWait(self.driver, 1.5).until(
                        ec.presence_of_element_located((By.CLASS_NAME, "some-plug-class"))
                    )
                    logging.info("Suddenly 'some-plug-class' was found")
                except TimeoutException:
                    logging.info(f"Successful await")

                # Сворачиваем календарь, чтобы можно было ввести номер группы и получить расписание на запрошенную дату
                actions = ActionChains(self.driver)
                actions.send_keys(Keys.ESCAPE).perform()

                # Ожидаем, чтобы прогрузить результат на странице
                try:
                    WebDriverWait(self.driver, 1.5).until(
                        ec.presence_of_element_located((By.CLASS_NAME, "some-plug-class"))
                    )
                    logging.info("Suddenly 'some-plug-class' was found")
                except TimeoutException:
                    logging.info(f"Successful await")

                # Теперь ищем поле ввода номера группы
                group_number_input = WebDriverWait(self.driver, 10).until(
                    ec.presence_of_element_located((By.ID, "rs-:Rlhr6:")))
                # отправляем значение номера группы в поле для ввода
                group_number_input.send_keys(str(group_number))

                # Ожидаем, чтобы прогрузить подсказку
                try:
                    WebDriverWait(self.driver, 5).until(
                        ec.presence_of_element_located((By.CLASS_NAME, "some-plug-class"))
                    )
                    logging.info("Suddenly 'some-plug-class' was found")
                except TimeoutException:
                    logging.info(f"Successful await")

                # выбираем предложенный вариант из списка
                group_number_input.send_keys(Keys.ARROW_DOWN)
                group_number_input.send_keys(Keys.ENTER)

                # Ожидаем, чтобы прогрузить результат
                try:
                    WebDriverWait(self.driver, 5).until(
                        ec.presence_of_element_located((By.CLASS_NAME, "some-plug-class"))
                    )
                    logging.info("Suddenly 'some-plug-class' was found")
                except TimeoutException:
                    logging.info(f"Successful await")

            except TimeoutException as e:
                logging.info(f"Элемент по CLASS_NAME 'rs-btn rs-btn-default' не найден: {e}")

        except TimeoutException as e:
            logging.info(f"Элемент по ID 'schedule_iframe' не найден: {e}")
        finally:

            # Возвращаемся на основную страницу (фрейм)
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

            # Closes the browser and shuts down the ChromiumDriver executable.
            self.driver.quit()
            # Возвращаем имя обрезанного скриншота, чтобы отправить его через бота и удалить
            return self.cropped_screenshot_name


# test_class = MireaScheduleParser()
# print(test_class.datetime_now_schedule_page_parser("УДМО-01-24"))
# print(test_class.particular_date_schedule_parser("УДМО-01-24", required_date="Март, 2025, 4"))