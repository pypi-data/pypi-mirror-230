"""Usage:
--------

    $ github_domain_scraper --link=<github_link> --json=filename

    where github_link is the URL of GitHub domain
    filename is the json file name. e.g. username.json

Version:
--------

- github-domain-scraper v1.0.2
"""
import argparse

from github_domain_scraper.link_extractor import LinkExtractor


def main():
    parser = argparse.ArgumentParser(description="GitHub Domain Scraper")
    parser.add_argument("--link", type=str, help="GitHub link to scrape", required=True)
    parser.add_argument("--json", type=str, help="JSON file to save results")

    args = parser.parse_args()

    github_link = args.link
    if not github_link:
        raise SystemExit()

    extractor = LinkExtractor(initial_link=github_link)
    result = extractor.extract(jsonfile=args.json)
    if not args.json:
        print(result)


if __name__ == "__main__":
    main()
