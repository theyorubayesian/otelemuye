import argparse
import json
import logging
import sys
from typing import Tuple

from scrapy.crawler import CrawlerRunner
from scrapy.settings import Settings
from scrapy.spiders import Spider
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
from twisted.internet.task import LoopingCall

from legit import spiders

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level="INFO",
)
logger = logging.getLogger(__name__)


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
    run_parser.add_argument("--job-dir", type=str, help="Job directory")
    run_parser.add_argument("--check-interval", type=int, help="Check if crawler is still running after defined interval (seconds)")

    args, _ = parser.parse_known_args()
    if args.config_file:
        config = json.load(open(args.config_file, "r"))
        args_dict = vars(args)
        args_dict.update(config)
    
    return args


def _is_running(output_file: str, line_count: int) -> Tuple[bool, int]:
    new_line_count = sum(1 for _ in open(output_file, "r"))
    return new_line_count > line_count, new_line_count


def start_crawl(spider_class: Spider, settings: Settings, interval: int):
    global line_count
    line_count = 0

    configure_logging(settings=settings)
    runner = CrawlerRunner(settings)
    d = runner.crawl(spider_class)

    # d = runner.join()
    d.addBoth(lambda _: reactor.stop())

    l = LoopingCall(ensure_completion, spider=spider_class, settings=settings, interval=interval)
    l.start(interval=interval, now=False)
    reactor.run()


def ensure_completion(spider: Spider, settings: Settings, interval: int):
    logging.info("Checking line count")
    global line_count
    running, line_count = _is_running(settings["OUTPUT_FILE"], line_count)
    
    if not running:
        logging.info("Scraping stopped running.")
        reactor.stop()

        logging.info("Restarting Crawl")
        # Restarting A Twisted Reactor: https://www.blog.pythonlibrary.org/2016/09/14/restarting-a-twisted-reactor/
        del sys.modules["twisted.internet.reactor"]

        from twisted.internet import reactor
        from twisted.internet import default
        default.install()

        start_crawl(spider, settings, interval)


def main():
    args = get_args()

    if args.command == "run-till-complete":
        settings = get_project_settings()
        # spider_class = getattr(module, import_module(args.spider_class, package="legit.spiders.crawler")
        spider_class = getattr(spiders, args.spider_class)

        start_crawl(spider_class, settings, args.check_interval)

    # TODO: Get Spider stats while running: 
    #  https://stackoverflow.com/questions/34799320/scrapy-get-or-flush-stats-while-spider-is-running


if __name__ == "__main__":
    main()
