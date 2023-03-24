import argparse
import json
import logging
import sys
from pathlib import Path

import yaml
from scrapy.settings import Settings
from scrapy.spiders import Spider
from scrapy.utils.project import get_project_settings

from otelemuye import spiders
from otelemuye.process import CustomCrawlerProcess as CrawlerProcess

# TODO: Advanced logging configuration
# https://stackoverflow.com/a/31838281
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level="INFO",
)
logger = logging.getLogger(__name__)
selenium_logger = logging.getLogger("selenium.webdriver.remote.remote_connection")
selenium_logger.setLevel(logging.WARNING)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="Otelemuye",
        description="Crawling websites for language datasets using Scrapy",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="Written by: Akintunde 'theyorubayesian' Oladipo <akin.o.oladipo@gmail.com>"
    )
    parser.add_argument("--config-file", type=str, help="Path to configuration for space")
    parser.add_argument("--verbose", type=bool, default=True, help="If True, print verbose output")

    sub_parser = parser.add_subparsers(dest="command", title="Commands", description="Valid commands")
    run_parser = sub_parser.add_parser("run-till-complete", help="Run crawler until all articles are collected.")
    run_parser.add_argument("--spider-class", type=str, help="Name of Spider class")
    run_parser.add_argument("--spider-config-file", type=str, help="File containing Spider class attributes to be set")
    run_parser.add_argument("--job-dir", type=str, help="Job directory")
    run_parser.add_argument("--check-interval", default=0, type=int, help="Check if crawler is still running after defined interval (seconds)")

    args, _ = parser.parse_known_args()
    if args.config_file:
        config = json.load(open(args.config_file, "r"))
        args_dict = vars(args)
        args_dict.update(config)
    
    if not args.spider_config_file:
        args.spider_config_file = f"config/{args.spider_class.lower().replace('spider', '')}.yaml"
    
    assert Path(args.spider_config_file).exists(), "`spider_config_file` is not set or does not exist"
    
    return args


def start_crawl(spider_class: str, settings: Settings, interval: int):
    process = CrawlerProcess(settings)
    process.crawl(spider_class)
    process.start(interval=interval)


def restart_crawl(
    spider_class: Spider, 
    settings: Settings, 
    interval: int
):
    # Restarting A Twisted Reactor: https://www.blog.pythonlibrary.org/2016/09/14/restarting-a-twisted-reactor/
    del sys.modules["twisted.internet.reactor"]

    from twisted.internet import reactor
    from twisted.internet import default
    default.install()

    start_crawl(spider_class, settings, interval)


def main():
    args = get_args()

    # TODO: Run multiple spiders
    if args.command == "run-till-complete":
        settings = get_project_settings()
        spider_class = getattr(spiders, args.spider_class)
        spider_class.set_spider_attributes(args.spider_config_file)

        start_crawl(spider_class, settings, args.check_interval)

        while True:
            if "RESTART_INDICATOR" in spider_class.custom_settings and \
            Path(spider_class.custom_settings["RESTART_INDICATOR"]).exists():
                restart_crawl(spider_class, settings, args.check_interval)
            else:
                break

    # TODO: Get spider stats. If finished_reason, restart spider
    # TODO: Get Spider stats while running: 
    # https://stackoverflow.com/questions/34799320/scrapy-get-or-flush-stats-while-spider-is-running
    # https://stackoverflow.com/questions/59141363/writing-scraping-stats-to-a-database-using-scrapy-statscollector
    # https://github.com/scrapy/scrapy/issues/845
    # https://stackoverflow.com/questions/12553117/how-to-filter-duplicate-requests-based-on-url-in-scrapy

if __name__ == "__main__":
    main()
