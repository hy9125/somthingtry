import asyncio
import cgi
from collections import namedtuple
import logging
import re
import time
from urllib import parse

from asyncio import Queue

import aiohttp

LOGGER = logging.getLogger(__name__)



def is_redirect(response):
    return response.status in (300, 301, 302, 303, 307)


FetchStatistic = namedtuple('FetchStatistic',
                            ['url',
                             'next_url',
                             'status',
                             'title',
                             'redirect',
                             'num_urls',
                             'num_new_urls'])


class Crawler:
    def __init__(self, roots,
                 exclude=None, strict=True,  # What to crawl.
                 max_redirect=10, max_tries=4,  # Per-url limits.
                 max_tasks=10, *, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.roots = roots
        self.exclude = exclude
        self.strict = strict
        self.max_redirect = max_redirect
        self.max_tries = max_tries
        self.max_tasks = max_tasks
        self.q = Queue(loop=self.loop)
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.seen_urls = set()
        self.done = []

        self.root_domains = set()
        for root in roots:
            parts = parse.urlparse(root)
            host, port = parse.splitport(parts.netloc)
            if not host:
                continue
            if re.match(r'\A[\d\.]*\Z', host):
                self.root_domains.add(host)
            else:
                host = host.lower()
                self.root_domains.add(host)
        for root in roots:
            self.add_url(root)

    def close(self):
        """Close resources."""
        self.session.close()

    def host_okay(self, host):
        host = host.lower()
        if host in self.root_domains:
            return True
        if re.match(r'\A[\d\.]*\Z', host):
            return False
        if self.strict:
            return self._host_okay_strictish(host)


    def _host_okay_strictish(self, host):
        host = host[4:] if host.startswith('www.') else 'www.' + host
        return host in self.root_domains

    def record_statistic(self, fetch_statistic):
        self.done.append(fetch_statistic)

    async def parse_links(self, response):
        links = set()

        if response.status == 200:
            content_type = response.headers.get('content-type')
            if isinstance(response.url, str):
                resp_url = response.url
            else:
                resp_url = response.url.scheme + '://' + response.url.host + response.url.path

            if content_type:
                content_type, pdict = cgi.parse_header(content_type)

            if content_type in ['text/html', 'application/xml']:
                text = await response.text()
                # Replace href with (?:href|src) to follow image links.
                urls = set(re.findall(r'''(?i)href=["']([^\s"'<>]+)''',text))
                if urls:
                    LOGGER.info('got %r distinct urls from %r',
                                len(urls), response.url.human_repr())
                for url in urls:
                    normalized = parse.urljoin(resp_url, url)
                    defragmented, frag = parse.urldefrag(normalized)
                    if self.url_allowed(defragmented):
                        print(url)
                        links.add(defragmented)

        stat = FetchStatistic(
            url=resp_url,
            next_url=None,
            redirect=11-self.max_redirect,
            status=response.status,
            num_urls=len(links),
            num_new_urls=len(links - self.seen_urls))

        return stat, links

    async def fetch(self, url, max_redirect):
        """Fetch one URL."""
        tries = 0
        while tries < self.max_tries:
            try:
                response = await self.session.get(url, allow_redirects=False)

                if tries > 1:
                    LOGGER.info('try %r for %r success', tries, url)

                break
            except aiohttp.ClientError as client_error:
                LOGGER.info('try %r for %r raised %r', tries, url, client_error)
            tries += 1
        else:
                    LOGGER.error('%r failed after %r tries',
                                 url, self.max_tries)
                    self.record_statistic(FetchStatistic(url=url,
                                                         next_url=None,
                                                         status=None,
                                                         title = '',
                                                         redirect=11-self.max_redirect,
                                                         num_urls=0,
                                                         num_new_urls=0))
                    return

        try:
            if is_redirect(response):
                location = response.headers['location']
                next_url = parse.urljoin(str(url), location)
                self.record_statistic(FetchStatistic(url=url,
                                                     next_url=next_url,
                                                     status=response.status,
                                                     title='',
                                                     redirect=11-self.max_redirect,
                                                     num_urls=0,
                                                     num_new_urls=0))

                if next_url in self.seen_urls:
                    return
                if max_redirect > 0:
                    LOGGER.info('redirect to %r from %r', next_url, url)
                    self.add_url(next_url, max_redirect - 1)
                else:
                    LOGGER.error('redirect limit reached for %r from %r',
                                 next_url, url)
            else:
                stat, links = await self.parse_links(response)
                self.record_statistic(stat)
                for link in links.difference(self.seen_urls):
                    self.q.put_nowait((link, self.max_redirect))
                self.seen_urls.update(links)
        finally:
            await response.release()

    async def work(self):
        try:
            while True:
                url, max_redirect = await self.q.get()
                assert url in self.seen_urls
                await self.fetch(url, max_redirect)
                self.q.task_done()
        except asyncio.CancelledError:
            pass

    def url_allowed(self, url):
        if self.exclude and re.search(self.exclude, url):
            return False
        parts = parse.urlparse(url)
        if parts.scheme not in ('http', 'https'):
            LOGGER.debug('skipping non-http scheme in %r', url)
            return False
        host, port = parse.splitport(parts.netloc)
        if not self.host_okay(host):
            LOGGER.debug('skipping non-root host in %r', url)
            return False
        return True

    def add_url(self, url, max_redirect=None):
        if max_redirect is None:
            max_redirect = self.max_redirect
        LOGGER.debug('adding %r %r', url, max_redirect)
        self.seen_urls.add(url)
        self.q.put_nowait((url, max_redirect))

    async def crawl(self):
        """Run the crawler until all finished."""
        workers = [asyncio.Task(self.work(), loop=self.loop)
                   for _ in range(self.max_tasks)]
        await self.q.join()
        for w in workers:
            w.cancel()



def main():
    """Main program.
    Parse arguments, set up event loop, run crawler, print report.
    """
    roots = ['http://www.baidu.com']
    loop = asyncio.SelectorEventLoop()
    asyncio.set_event_loop(loop)
    crawler = Crawler(roots)
    loop.run_until_complete(crawler.crawl())
    crawler.close()
    loop.stop()
    loop.run_forever()

    loop.close()


if __name__ == '__main__':
    main()
