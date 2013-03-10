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

@register_scraper
class VergeScraper(ReviewScraper):
    site_name = "TheVerge"

    def __init__(self, url):
        super(self.__class__, self).__init__(url)

    @classmethod
    def matches_url(cls, url):
        return "theverge.com" in url

    def parse_page(self):
        self.download_page()
        try:
            self.score = \
                float(self.soup.find(class_="product-score-verge").strong.text)
        except:
            print "Unable to find score on given page"

@register_scraper
class CNETScraper(ReviewScraper):
    site_name = "CNET"

    def __init__(self, url):
        super(self.__class__, self).__init__(url)

    @classmethod
    def matches_url(cls, url):
        return "cnet.com" in url

    def parse_page(self):
        self.download_page()
        try:
            self.score = \
                float(self.soup.find(class_="rateBarStyle").strong.text)
        except:
            print "Unable to find score on given page"

@register_scraper
class GdgtScraper(ReviewScraper):
    site_name = "Gdgt"

    def __init__(self, url):
        super(self.__class__, self).__init__(url)

    @classmethod
    def matches_url(cls, url):
        return "gdgt.com" in url

    def parse_page(self):
        self.download_page()
        try:
            self.score = \
                float(self.soup.find(class_="new-gdgt-score").text) / 10
        except:
            print "Unable to find score on given page"

@register_scraper
class PCMagScraper(ReviewScraper):
    site_name = "PCMag"

    def __init__(self, url):
        super(self.__class__, self).__init__(url)

    @classmethod
    def matches_url(cls, url):
        return "pcmag.com" in url

    def parse_page(self):
        self.download_page()
        try:
            self.score = \
                float(self.soup.find(class_="rating").span['title'])*2
        except:
            print "Unable to find score on given page"

if __name__ == "__main__":
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
