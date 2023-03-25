import logging
import os
from typing import Tuple

from scrapy.crawler import CrawlerProcess
from scrapy.utils.misc import create_instance
from scrapy.utils.misc import load_object
from scrapy.utils.ossignal import install_shutdown_handlers
from scrapy.settings import Settings
from twisted.internet.task import LoopingCall
from twisted.python.log import err

logger = logging.getLogger(__name__)


class CustomCrawlerProcess(CrawlerProcess):
    """
    Overrides `CrawlerProcess` to insert a LoopingCall that ensures scraping is still running.
    CrawlerProcess is still initialized as normal. LoopingCall is inserted when `start` is called with interval > 0
    """
    def start(
            self, 
            interval: int = 0, 
            line_count: int = 0, 
            stop_after_crawl: bool = True, 
            install_signal_handlers: int = True
        ):
        from twisted.internet import reactor

        if stop_after_crawl:
            d = self.join()
            # Don't start the reactor if the deferreds are already fired
            if d.called:
                return
            d.addBoth(self._stop_reactor)

        if install_signal_handlers:
            install_shutdown_handlers(self._signal_shutdown)
        resolver_class = load_object(self.settings["DNS_RESOLVER"])
        resolver = create_instance(resolver_class, self.settings, self, reactor=reactor)
        resolver.install_on_reactor()
        tp = reactor.getThreadPool()
        tp.adjustPoolsize(maxthreads=self.settings.getint("REACTOR_THREADPOOL_MAXSIZE"))
        
        # ------------------------
        # Additional functionality
        # ------------------------
        if interval:
            self.ls = []
            for idx, crawler in enumerate(list(self.crawlers)):
                try:
                    os.remove(crawler.settings["RESTART_INDICATOR"])
                except OSError:
                    pass

                self.line_count = line_count
                l = LoopingCall(
                    self.ensure_completion,
                    settings=crawler.settings,
                    crawler_idx=idx
                )
                self.ls.append(l)
                ld = l.start(interval=interval, now=False)
                ld.addErrback(err)
        # ------------------------

        reactor.addSystemEventTrigger("before", "shutdown", self.stop)
        reactor.run(installSignalHandlers=False)  # blocking call

    @staticmethod
    def _is_running(output_file: str, line_count: int) -> Tuple[bool, int]:
        new_line_count = sum(1 for _ in open(output_file, "r"))
        return new_line_count > line_count, new_line_count
    
    def _graceful_stop_reactor(self):
        if hasattr(self, "ls"):
            _ = [l.stop() for l in self.ls]
        
        return super()._graceful_stop_reactor()

    def ensure_completion(self, settings: Settings, crawler_idx: int):
        logger.info("Checking line count")

        running, line_count = self._is_running(settings["OUTPUT_FILE"], self.line_count)
        self.line_count = line_count

        if not running:
            logger.info("Scraping stopped running.")
            from twisted.internet import reactor
            # TODO: Stop the particular crawler rather than reactor?
            reactor.callFromThread(self._graceful_stop_reactor)

            open(settings["RESTART_INDICATOR"], "w").close()
