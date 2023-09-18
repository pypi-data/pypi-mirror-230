from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class SeleniumWebDriver:
    def __init__(self, download_path=None):
        self.web_driver = None
        self.download_path = download_path

    @property
    def options(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--headless")

        if self.download_path:
            options.add_experimental_option('prefs', {'download.default_directory': self.download_path})

        return options

    @property
    def webdriver(self):
        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=self.options
        )
