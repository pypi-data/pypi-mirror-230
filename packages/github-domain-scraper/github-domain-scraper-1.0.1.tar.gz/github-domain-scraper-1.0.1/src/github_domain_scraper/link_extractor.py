import json
import os
import sys

from github_domain_scraper.logger import get_logger
from github_domain_scraper.parser import GithubBackend

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logger = get_logger(__file__)


class LinkExtractor:
    github_domain = 'https://github.com/'

    def __init__(self, initial_link: str, total_links_to_download: int = sys.maxsize):
        self.initial_link = initial_link
        self.total_links_to_download = total_links_to_download

    def extract(self, jsonfile=None):
        logger.info('Extracting...')
        parser = GithubBackend(total_links_to_download=self.total_links_to_download)
        result = parser.process(url=self.initial_link)

        if jsonfile:
            with open(jsonfile, "w") as file:
                json.dump(result, file, indent=4)
            logger.info(f'Saved links to {jsonfile}')
        else:
            return result
