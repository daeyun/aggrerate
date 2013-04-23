from bs4 import UnicodeDammit
from datetime import datetime
import itertools

from aggrerate.scraper import ReviewScraper, register_scraper
from aggrerate import util

@register_scraper
class VergeScraper(ReviewScraper):
    site_name = "TheVerge"
    pretty_site_name = "The Verge"

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
            self.blurb = \
                self.soup.find(class_="conclusion").find(class_="big").text.strip()
            self.body = \
                util.strip_tags(str(self.soup.find(class_="entry-content")))
            # We can write this as a string straight into the db
            self.timestamp = \
                self.soup.time['datetime']
        except:
            print "Unable to find score on given page"

@register_scraper
class CNETScraper(ReviewScraper):
    pretty_site_name = site_name = "CNET"

    def __init__(self, url):
        super(self.__class__, self).__init__(url)

    @classmethod
    def matches_url(cls, url):
        return "cnet.com" in url

    def parse_page(self):
        self.download_page()
        try:
            rate_bar_elem = self.soup.find(class_="rateBarStyle")
            if rate_bar_elem:
                self.score = float(rate_bar_elem.strong.text)
            else:
                self.score = 2*float(self.soup.find(class_="rating").text)
            self.blurb = \
                self.soup.find(class_="theBottomLine").span.text.strip()
            self.body = \
                util.strip_tags(str(self.soup.find(id="contentBody")))
            self.timestamp = \
                self.soup.time['datetime']
        except:
            print "Unable to find score on given page"

@register_scraper
class GdgtScraper(ReviewScraper):
    pretty_site_name = site_name = "Gdgt"

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

            # There is no publish date for gdgt, but it is a composite score
            # anyways. We consider the composite score to be valid on the date
            # that the last review was published.
            self.timestamp = \
                sorted(map(lambda t: datetime.strptime(t.contents[2].strip(), "%b %d, %Y").strftime("%Y-%m-%d"),
                    self.soup.find(id='critic-reviews-stream').find_all('header')))[-1]

            # Sometimes they don't have a blurb, so let this fail last
            self.body = \
                util.strip_tags(str(self.soup.find(class_="gdgt-says")))
            self.blurb = \
                ' '.join(itertools.chain(
                    self.soup.find(class_="gdgt-says").h2.stripped_strings))
        except:
            print "Unable to find score on given page"

@register_scraper
class PCMagScraper(ReviewScraper):
    site_name = "PCMag"
    pretty_site_name = "PCMag.com"

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
            self.blurb = \
                self.soup.find("meta", property="og:description")['content']
            self.body = \
                util.strip_tags(str(self.soup.find(class_="pros-cons-bl")) +
                                str(self.soup.find(class_="review-body")))
            self.timestamp = \
                datetime.strptime(self.soup.find(class_="dtreviewed").text.strip(),
                    "%B %d, %Y").strftime("%Y-%m-%d")
        except:
            print "Unable to find score on given page"

@register_scraper
class WiredScraper(ReviewScraper):
    pretty_site_name = site_name = "Wired"

    def __init__(self, url):
        super(self.__class__, self).__init__(url)

    @classmethod
    def matches_url(cls, url):
        return "wired.com" in url

    def parse_page(self):
        self.download_page()
        try:
            self.score = float(self.soup.find("span", class_="rating").text. \
                split(' ')[1].split('/')[0])
            self.blurb = self.soup.find(class_="explanation").text
            self.body = \
                util.strip_tags(str(self.soup.find(class_="entry")))

            self.timestamp = \
                filter(lambda x: x.has_key('name') and x['name'] == 'DisplayDate',
                    self.soup.find_all("meta"))[0]['content']
        except:
            print "Unable to find score on given page"
