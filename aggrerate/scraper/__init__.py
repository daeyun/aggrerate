import urllib2
from urlparse import urlparse

from bs4 import BeautifulSoup
import MySQLdb as mdb

class ReviewScraper(object):
    scrapers = []

    def __init__(self, url):
        self.url   = url
        self.soup  = None
        self.score = None

    @classmethod
    def from_url(cls, url):
        domain = urlparse(url).netloc
        for scraper in cls.scrapers:
            if scraper.matches_url(url):
                return scraper(url)

    def download_page(self):
        if self.soup is not None:
            return

        try:
            p = urllib2.urlopen(self.url, None)

            # We use Python's builtin HTML parser instead of lxml because lxml
            # seems to fail partway through parsing some pages (because of
            # errors? size? not sure)
            self.soup = BeautifulSoup(p.read(), "html.parser")
        except:
            print "Failed to download page '%s'" % self.url

    def parse_page(self):
        raise NotImplementedError

    def __str__(self):
        return '%s(%s)' % (self.__class__.site_name, self.score)

def register_scraper(scraper):
    ReviewScraper.scrapers.append(scraper)

# We don't use anything from this module, but the classes there are registered
# into our list of scrapers
import aggrerate.scraper.site_scrapers

def test():
    urls = [
        "http://www.theverge.com/2012/11/2/3589280/google-nexus-4-review",
        "http://www.theverge.com/2012/11/1/3584486/nokia-lumia-920-review",
        "http://reviews.cnet.com/samsung-galaxy-s3-review/",
        "http://gdgt.com/apple/iphone/5/",
        "http://www.pcmag.com/article2/0,2817,2414819,00.asp"
    ]

    for url in urls:
        scraper = ReviewScraper.from_url(url)
        if scraper:
            scraper.parse_page()
            print scraper
        else:
            print "Couldn't find scraper :("
