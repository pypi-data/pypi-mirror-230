import os
import sys

import undetected_chromedriver as uc
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class ChatGPTDriver(uc.Chrome):
    """
    Custom selenium driver for ChatGPT.
    ##### Still in development.
    """

    def __init__(self, options: uc.ChromeOptions, headless: bool = False):
        caps = DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'performance': 'ALL'}

        # 检查应用是否被打包
        if getattr(sys, 'frozen', False):
            # 应用被打包为 .exe
            bundle_dir = sys._MEIPASS
        else:
            # 应用在常规Python环境下运行
            bundle_dir = os.path.dirname(os.path.abspath(__file__))

        chromedriver_path = os.path.join(bundle_dir, 'LineAuthGPT', 'internal', 'chromedriver.exe')


        super().__init__(driver_executable_path=chromedriver_path, options=options, headless=headless,
                         desired_capabilities=caps)

    def safe_click(self, mark, timeout: int = 10) -> bool:
        """
        Clicks an element, and if it fails, tries again.

        Args:
        ----------
            mark: (By, str): The element to click.
            timeout: (int): The amount of time to wait for the element to be clickable.

        Returns:
        ----------
            bool: Whether or not the element was clicked.
        """
        wait = WebDriverWait(self, timeout)
        try:
            wait.until(EC.visibility_of_element_located(mark))
            element = wait.until(EC.element_to_be_clickable(mark))
            element.click()
        except:
            return False
        else:
            return True
