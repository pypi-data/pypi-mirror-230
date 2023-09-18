# github-domain-scraper

The `github-domain-scraper` is a powerful tool for extracting valuable information from GitHub domains. It provides a
wide
variety of use-cases, making it a versatile solution for various scenarios.

## Installation

You can install the `github-domain-scraper` from [PyPI](https://pypi.org/project/realpython-reader/):

    python -m pip install github-domain-scraper

The reader is supported on Python 3.8 and above.

## How to use

The `github-domain-scraper` is having wide variety of use-cases

### Command-line Tool

You can use the `github-domain-scraper` as a command-line tool to extract information from GitHub domains:

   ```
   python -m github_domain_scraper --link=https://github.com/Parth971
   ```

You can also specify a JSON output file for the results:

   ```
   python -m github_domain_scraper --link=https://github.com/Parth971 --json=repo.json
   ```

### Integration in Python Modules

The `github-domain-scraper` can also be seamlessly integrated into other Python modules.
Import the `LinkExtractor` class from `github_domain_scraper.link_extractor` and use it as
follows:

   ```python
   from github_domain_scraper.link_extractor import LinkExtractor

links = LinkExtractor(initial_link="github_link").extract()
   ```

This makes it easy to incorporate github-domain-scraper functionality into your custom Python projects.

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.

