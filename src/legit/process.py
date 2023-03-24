import logging
import os
from typing import Tuple

from scrapy.crawler import CrawlerProcess
from scrapy.utils.misc import create_instance, load_object
from scrapy.utils.ossignal import install_shutdown_handlers
from scrapy.settings import Settings
from twisted.internet.task import LoopingCall
from twisted.python.log import err

logger = logging.getLogger(__name__)


class CustomCrawlerProcess(CrawlerProcess):
    def start(self, interval, line_count=0, stop_after_crawl=True, install_signal_handlers=True):
        """
        This method starts a :mod:`~twisted.internet.reactor`, adjusts its pool
        size to :setting:`REACTOR_THREADPOOL_MAXSIZE`, and installs a DNS cache
        based on :setting:`DNSCACHE_ENABLED` and :setting:`DNSCACHE_SIZE`.

        If ``stop_after_crawl`` is True, the reactor will be stopped after all
        crawlers have finished, using :meth:`join`.

        :param bool stop_after_crawl: stop or not the reactor when all
            crawlers have finished

        :param bool install_signal_handlers: whether to install the shutdown
            handlers (default: True)
        """
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
        
        try:
            os.remove(self.settings["RESTART_INDICATOR"])
        except OSError:
            pass

        self.line_count = line_count
        self.l = LoopingCall(
            self.ensure_completion,
            settings=self.settings
        )
        ld = self.l.start(interval=interval, now=False)
        ld.addErrback(err)

        reactor.addSystemEventTrigger("before", "shutdown", self.stop)
        reactor.run(installSignalHandlers=False)  # blocking call

    @staticmethod
    def _is_running(output_file: str, line_count: int) -> Tuple[bool, int]:
        new_line_count = sum(1 for _ in open(output_file, "r"))
        return new_line_count > line_count, new_line_count
    
    def _graceful_stop_reactor(self):
        self.l.stop()
        return super()._graceful_stop_reactor()

    def crawl(self, crawler_or_spidercls, *args, **kwargs):
        self.spidercls = crawler_or_spidercls
        return super().crawl(crawler_or_spidercls, *args, **kwargs)

    def ensure_completion(self, settings: Settings):
        logger.info("Checking line count")

        running, line_count = self._is_running(settings["OUTPUT_FILE"], self.line_count)
        self.line_count = line_count

        if not running:
            logger.info("Scraping stopped running.")
            from twisted.internet import reactor
            reactor.callFromThread(self._graceful_stop_reactor)

            open(settings["RESTART_INDICATOR"], "w").close()
