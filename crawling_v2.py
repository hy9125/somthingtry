import asyncio
import cgi
from collections import namedtuple
import logging
import re
from urllib import parse
from lxml import etree
from asyncio import Queue
import aiohttp
import pymongo

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def is_redirect(response):
    return response.status in (300, 301, 302, 303, 307)


FetchStatistic = namedtuple('FetchStatistic',
                            ['url',
                             'sub_urls',
                             'status',
                             'title',
                             'cur_depth'])


class Crawler:
    def __init__(self, roots,
                 max_cur_depth=5, max_tries=4,  # Per-url limits.
                 max_tasks=20, *, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.roots = roots
        self.max_cur_depth = max_cur_depth
        self.max_tries = max_tries
        self.max_tasks = max_tasks
        self.q = Queue(loop=self.loop)
        self.headers = {
            'Connection': 'Keep-Alive',
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'
        }
        self.session = aiohttp.ClientSession(headers=self.headers)
        self.seen_urls = set()
        self.done = []
        self.root_domains = 'dianrong.com'
        self.collection = pymongo.MongoClient('127.0.0.1', )
        self.db = self.collection.dataportal
        self.i = 0
        for root in roots:
            self.seen_urls.add(root)
            self.q.put_nowait((root, self.max_cur_depth))

    def close(self):
        self.session.close()

    def record_statistic(self, fetch_statistic):
        # c = motor.MotorClient('/tmp/mongodb-5281.sock', max_pool_size=1000)
        # db = c.test_database

        self.db.sitemap.save({
            'url': fetch_statistic.url,
            'sub_urls': list(fetch_statistic.sub_urls),
            'status': fetch_statistic.status,
            'title': fetch_statistic.title,
            'cur_depth': fetch_statistic.cur_depth,
        })

    async def parse_links(self, response, cur_depth):
        links = set()
        real_title = 'error page'
        if isinstance(response.url, str):
            resp_url = response.url
        else:
            resp_url = response.url.scheme + '://' + \
                       response.url.host + response.url.path

        if response.status == 200:
            content_type = response.headers.get('content-type')
            if content_type:
                content_type, _ = cgi.parse_header(content_type)
            if content_type in ('text/html', 'application/xml'):
                text = await response.text()
                doc = etree.HTML(text)
                title = doc.xpath('//head/title/text()')
                if title:
                    real_title = title[0]
                sub_nodes = doc.xpath('//*[@href]')
                for sub_node in sub_nodes:
                    sub_url = sub_node.xpath('./@href')
                    if sub_url:
                        Flag = True
                        sub_url = sub_url[0]
                        real_url = parse.urljoin(resp_url, sub_url)
                        # 避免参数传递异常
                        abs_url = real_url.split('?')[0]
                        if self.root_domains not in abs_url:
                            continue
                        for filter_tag in ['.js', '.css', '.img', '.png', '.gif', '.jpg', '.ico', '.jpg', '.jpeg',
                                           '.png', '.pdf']:
                            if abs_url.endswith(filter_tag):
                                Flag = False
                        if Flag:
                            defragmented, frag = parse.urldefrag(real_url)
                            if self.url_allowed(defragmented):
                                links.add(defragmented)

        stat = FetchStatistic(
            url=resp_url,
            sub_urls=links,
            status=response.status,
            title=real_title,
            cur_depth=cur_depth)

        return stat, links

    async def fetch(self, url, cur_depth):
        """Fetch one URL."""
        tries = 0
        while tries < self.max_tries:
            try:
                response = await self.session.get(url, headers=self.headers, allow_redirects=False)
                break
            except aiohttp.ClientError as client_error:
                LOGGER.info('try %r for %r raised %r', tries, url, client_error)
            tries += 1
        else:
            return
        try:
            if is_redirect(response):
                location = response.headers['location']
                next_url = parse.urljoin(url, location)
                self.record_statistic(FetchStatistic(url=url,
                                                     sub_urls=set(),
                                                     status=response.status,
                                                     title='redirect page',
                                                     cur_depth=cur_depth))

                if next_url in self.seen_urls:
                    return
                self.q.put_nowait((next_url, cur_depth))
            else:
                stat, links = await self.parse_links(response, cur_depth)
                self.record_statistic(stat)
                for link in links.difference(self.seen_urls):
                    self.q.put_nowait((link, cur_depth))
                    print(link)
                self.seen_urls.update(links)
        finally:
            await response.release()

    def url_allowed(self, url):
        # if self.exclude and re.search(self.exclude, url):
        #     return False
        parts = parse.urlparse(url)
        if parts.scheme not in ('http', 'https'):
            LOGGER.debug('skipping non-http scheme in %r', url)
            return False
        return True

    async def work(self):
        try:
            while True:
                url, cur_depth = await self.q.get()
                await self.fetch(url, cur_depth)
                self.q.task_done()
        except asyncio.CancelledError:
            pass

    async def crawl(self):
        """Run the crawler until all finished."""
        workers = [asyncio.Task(self.work(), loop=self.loop)
                   for _ in range(self.max_tasks)]
        await self.q.join()
        for w in workers:
            w.cancel()


if __name__ == '__main__':
    roots = ['https://www.dianrong.com']
    loop = asyncio.get_event_loop()
    crawler = Crawler(roots)
    try:
        loop.run_until_complete(crawler.crawl())
    finally:
        crawler.close()

