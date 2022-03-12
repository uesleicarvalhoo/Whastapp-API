import logging
import os
import tempfile
from contextlib import suppress
from functools import wraps
from typing import Any, Callable, Dict, List, Tuple, Union

from PIL import Image, ImageOps
from pydantic import validate_arguments
from selenium import webdriver
from selenium.common.exceptions import (ElementClickInterceptedException, NoSuchElementException,
                                        StaleElementReferenceException, TimeoutException)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdrivermanager import ChromeDriverManager

from src.constants import (BUTTON_ADD_MEDIA, BUTTON_ATTACHMENT, BUTTON_SEND_MESSAGE, CONTACT_BUTTON_CLOSE,
                           CONTACT_DETAILS, CONTACT_INFO, CONTACT_NAME, CONVERSE_DETAIL, ICON_UNREAD_MESSAGE,
                           MESSAGE_BOX, MESSAGE_INPUT, MESSAGE_PANEL, MESSAGE_TEXT, MESSAGES, QRCODE, RELOAD_QRCODE)
from src.schemas.contact import WhatsappContact
from src.schemas.message import MessageInput, MessageOutput
from src.settings import WHATSAPP_WAIT_CHECK_LOGGED
from src.utils.decorators import retry


class WhatsappTalker:
    __base_url = 'https://web.whatsapp.com/send?1=pt_BR&phone=%s'
    __callback_unread_message: List[Tuple[Callable, List[Any], Dict]] = []

    def __init__(self):
        logging.info("Updating Webdriver..")
        self.__driver_path = ChromeDriverManager().download_and_install()[0]
        self.__start_driver()

    def __start_driver(self) -> None:
        options = webdriver.ChromeOptions()
        # options.add_argument('user-data-dir=./web')
        options.add_argument(
            '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'  # noqa
        )
        options.add_argument('--headless')
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--start-maxized")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-log')
        options.add_argument('--loglevel=3')

        self.driver = webdriver.Chrome(self.__driver_path, options=options)
        self.driver.get('https://web.whatsapp.com/')

    @property
    @retry(stop_after=WHATSAPP_WAIT_CHECK_LOGGED, value_if_error=False, exceptions=(TimeoutException))
    def is_logged(self) -> bool:
        self.driver.save_screenshot("loggin.png")
        try:
            self.__get_element(MESSAGE_PANEL, 1)

        except TimeoutException:
            self.__get_element(QRCODE, 1)
            return False

        else:
            return True

    @validate_arguments
    def send_message(self, message: MessageInput) -> MessageOutput:
        if not self.validate_contact(message.contact):
            return MessageOutput(**{"success": False, "message": message, "reason": "Invalid contact"})

        if message.media:
            self.attach_media(message.media)

        if message.text:
            self.write_message(message.text)

        self.__get_element(BUTTON_SEND_MESSAGE).click()

        return MessageOutput(**{"success": True, "message": message})

    def write_message(self, message: str) -> None:
        msg_input = self.__get_element(MESSAGE_BOX).find_element_by_css_selector(MESSAGE_INPUT)

        for row in message.split('\n'):
            msg_input.send_keys(row)
            webdriver.ActionChains(self.driver).key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT).perform()

    def attach_media(self, media: str) -> None:
        self.__get_element(BUTTON_ATTACHMENT).click()
        self.__get_element(BUTTON_ADD_MEDIA, 20).send_keys(media)

    @retry(stop_after=30, value_if_error=False, exceptions=(TimeoutException, StaleElementReferenceException))
    @validate_arguments
    def validate_contact(self, contact: WhatsappContact) -> bool:
        self.driver.get(self.__base_url % contact.number)

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, MESSAGE_PANEL)))

        try:
            self.__get_element(CONTACT_INFO)

        except NoSuchElementException:
            return False

        else:
            return True

    def get_contact_info(self) -> WhatsappContact:
        @retry(stop_after=10, value_if_error=None, exceptions=(ValueError))
        def get_number() -> int:
            return int("".join([x for x in self.__get_all_elements(CONTACT_DETAILS)[4].text if x.isnumeric()]))

        @retry(stop_after=10, value_if_error=None, exceptions=(ValueError))
        def get_name() -> int:
            if name := self.__get_element(CONTACT_NAME).text:
                return name

            raise ValueError("Invalid name")

        with suppress(ElementClickInterceptedException):
            self.__get_element(CONTACT_INFO).click()
        self.__get_element(CONTACT_BUTTON_CLOSE).click()

        return WhatsappContact(**{"name": get_name(), "number": get_number()})

    def get_contact_info_by_number(self, number: int) -> WhatsappContact:
        self.driver.get(self.__base_url % number)
        return self.get_contact_info()

    def get_qrcode(self) -> str:
        if (
            'Clique para carregar o código QR novamente' in self.driver.page_source
            or 'Click to reload QR code' in self.driver.page_source
        ):
            self.__get_element(RELOAD_QRCODE)

        qr = self.__get_element(QRCODE)
        ActionChains(self.driver).move_to_element(qr).perform()

        folder, img = tempfile.mkstemp(prefix='qrcode', suffix='.png')
        qr.screenshot(img)
        os.close(folder)

        qr = ImageOps.expand(Image.open(img), border=50, fill='white')
        qr.save(img)

        return img

    @retry(stop_after=5, value_if_error=None, exceptions=(ValueError))
    def get_last_message(self) -> Union[str, None]:
        last_message = None
        for msg in self.driver.find_elements_by_css_selector(MESSAGES):
            with suppress(NoSuchElementException, StaleElementReferenceException):
                if text := msg.find_element_by_css_selector(MESSAGE_TEXT).text:
                    last_message = text

        if not last_message:
            raise ValueError("No message found!")

        return last_message

    def check_unread_message(self) -> Union[str, None]:
        try:
            self.__get_element(ICON_UNREAD_MESSAGE).click()

        except (NoSuchElementException, StaleElementReferenceException, TimeoutException):
            return None

        else:
            self.__get_element(CONTACT_INFO).click()
            converse_detail = self.__get_element(CONVERSE_DETAIL).text.lower()

            if "grupo" in converse_detail or "group" in converse_detail:
                return None

            return MessageInput(**{"text": self.get_last_message(), "contact": self.get_contact_info()})

    def refresh(self) -> None:
        self.driver.refresh()

    def call_on_unread_message(self, *args, **kwargs) -> Callable:
        def callable_decorator(fn: Callable):
            @wraps(fn)
            def decorated_function(*fn_args) -> Any:
                return fn(*fn_args, *args, **kwargs)

            self.__callback_unread_message.append((fn, args, kwargs))

            return decorated_function

        return callable_decorator

    def loop_to_check_unread_messages(self) -> None:
        while True:
            if not self.is_logged:
                logging.error("Check connection!")
                self.refresh()
                continue

            if msg := self.check_unread_message():
                for fn, args, kwargs in self.__callback_unread_message:
                    fn(msg, *args, **kwargs)
                self.refresh()

            # except MaxRetryError:
            #     logging.error("Restarting webdriver!")
            #     self.call_on_driver_error()
            #     self.__start_driver()

            # except Exception as e:
            #     logging.error("Error while check for unread messages, description: %s" % e)
            #     self.refresh()

    def __get_element(self, css_selector: str, timeout: int = 10):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
        )

    def __get_all_elements(self, css_selector: str, timeout: int = 10):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, css_selector))
        )

    def call_on_driver_error(self):
        pass
