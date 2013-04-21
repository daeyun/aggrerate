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
        self.blurb = None
        self.body  = None
        self.timestamp = None

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
            # 
            # Updated: for some reason, the builtin HTML parser didn't work
            # but lxml worked.
            self.soup = BeautifulSoup(p.read(), "lxml")
            # self.soup = BeautifulSoup(pp, "html.parser")
        except:
            print "Failed to download page '%s'" % self.url

    def parse_page(self):
        raise NotImplementedError

    def __str__(self):
        return '%s(%s, %s)' % (self.__class__.site_name, self.score, self.timestamp)

def register_scraper(scraper):
    ReviewScraper.scrapers.append(scraper)

# We don't use anything from this module, but the classes there are registered
# into our list of scrapers
import aggrerate.scraper.site_scrapers
