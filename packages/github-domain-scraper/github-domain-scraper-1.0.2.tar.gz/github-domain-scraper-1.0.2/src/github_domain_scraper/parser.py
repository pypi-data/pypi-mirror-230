import contextlib
import re
import time
from abc import ABC, abstractmethod

from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from github_domain_scraper.logger import get_logger
from github_domain_scraper.driver import SeleniumWebDriver

logger = get_logger(__file__)


class Backend(ABC):

    @abstractmethod
    def process(self, url):
        pass


class Link(ABC):

    @abstractmethod
    def is_url_matched(self):
        pass

    @property
    @abstractmethod
    def meta(self):
        pass


class UserRepositoriesLink(Link):
    pattern = r'(https://github.com/[\w-]+)/?(\?tab=[\w-]+)?'

    def __init__(self, url: str):
        self.url = url

    def is_url_matched(self) -> bool:
        return bool(re.match(self.pattern, self.url))

    @property
    def meta(self) -> dict:
        url = re.match(self.pattern, self.url).group(1)
        return {
            'url': f"{url}?tab=repositories",
            'xpath': '//div[@id="user-repositories-list"]/ul/li/div/div/h3/a[@href]',
            'next_xpath': '//a[@class="next_page"]'
        }


class SearchRepositoryLink(Link):
    pattern = r'https://github.com/search'

    def __init__(self, url: str):
        self.url = url

    def is_url_matched(self) -> bool:
        return bool(re.match(self.pattern, self.url))

    @property
    def meta(self) -> dict:
        return {
            'url': self.url,
            'xpath': '//div[@data-testid="results-list"]//div[contains(@class, "search-title")]/a[@href]',
            'next_xpath': '//a[text()="Next"]'
        }


class GithubBackend(Backend):
    link_classes = [
        UserRepositoriesLink,
        SearchRepositoryLink
    ]
    webdriver_waiting_time = 10

    def __init__(
            self,
            total_links_to_download: int,
            banned_waiting_time: int = 30
    ):
        self.wd = SeleniumWebDriver().webdriver
        # self.wd_wait = WebDriverWait(self.wd, self.webdriver_waiting_time)
        self.total_links_to_download = total_links_to_download
        self.banned_waiting_time = banned_waiting_time
        self.links = []

    def process(self, url: str) -> list:
        for link_class in self.link_classes:
            link_object = link_class(url=url)
            if link_object.is_url_matched():
                logger.debug(f'URL matched for {link_object.__class__.__name__} class')
                try:
                    self._start(link_object)
                except NotImplementedError as e:
                    logger.error(e)
                break
        else:
            logger.error('Provided link does not support extraction yet. Please contact package owner to add feature.')

        return self.links

    def _start(self, link_object: Link):
        link = link_object.meta.get('url')
        if not link:
            raise NotImplementedError(
                f"meta property method of {link_object.__class__.__name__} class "
                f"have not implemented correctly. It must return a dict with 'url' key."
            )

        try:
            self.wd.get(link)
            self.wd.switch_to.window(self.wd.window_handles[-1])
            while link and len(self.links) < self.total_links_to_download:
                logger.info(f'Crawling url {link}')
                next_link = self._parse(link_object=link_object)
                if self._is_banned:
                    logger.info(f'Banned!! Script will retry after {self.banned_waiting_time} seconds')
                    time.sleep(self.banned_waiting_time)
                    self.wd.get(link)
                else:
                    link = next_link
                    time.sleep(1)
        except KeyboardInterrupt:
            logger.error('Stopping crawler...')
        finally:
            self.wd.quit()
            logger.info('Crawler Stopped')

    @property
    def _is_banned(self):
        return (
                bool(self.wd.find_elements(By.XPATH, "//title[contains(text(),'Rate limit')]")) or
                bool(self.wd.find_elements(By.XPATH, "//title[contains(text(),'Error 429')]"))
        )

    def _parse(self, link_object: Link):
        element = link_object.meta.get('xpath')
        if not element:
            raise NotImplementedError(
                f"meta property method of {link_object.__class__.__name__} class "
                f"have not implemented correctly. It must return a dict with 'xpath' key."
            )

        try:
            WebDriverWait(self.wd, self.webdriver_waiting_time).until(
                expected_conditions.presence_of_all_elements_located((By.XPATH, element))
            )
        except TimeoutException:
            logger.error(f'Error in detecting links using xpath - {element}')
            return None

        repositories = [elem.get_attribute("href") for elem in self.wd.find_elements(By.XPATH, element)]
        self.links.extend(repositories)

        next_page_element = self.get_next_page_element(link_object=link_object)
        if next_page_element:
            next_page_element.click()
            time.sleep(1)
            return self.wd.current_url

    def get_next_page_element(self, link_object: Link):
        next_xpath = link_object.meta.get('next_xpath')
        if not next_xpath:
            raise NotImplementedError(
                f"meta property method of {self.__class__.__name__} class "
                f"have not implemented correctly. It must return a dict with 'next_xpath' key."
            )

        with contextlib.suppress(NoSuchElementException):
            return self.wd.find_element(By.XPATH, next_xpath)
