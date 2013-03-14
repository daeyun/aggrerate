from bs4 import UnicodeDammit
import itertools

from aggrerate.scraper import ReviewScraper, register_scraper

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
                '\n\n'.join(itertools.chain(
                    self.soup.find(class_="conclusion").stripped_strings
                ))
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
            self.score = \
                float(self.soup.find(class_="rateBarStyle").strong.text)
            self.blurb = \
                self.soup.find(class_="theBottomLine").span.text.strip()
            self.body = \
                '\n\n'.join(itertools.chain(
                    self.soup.find(id="reviewSummary").stripped_strings,
                    self.soup.find(id="editorReview").stripped_strings
                ))
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
            self.blurb = \
                ' '.join(itertools.chain(
                    self.soup.find(class_="gdgt-says").h2.stripped_strings))
            self.body = \
                '\n\n'.join(itertools.chain(
                    self.soup.find(class_="gdgt-says").stripped_strings
                ))
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
                '\n\n'.join(itertools.chain(
                    self.soup.find(class_="review-body").stripped_strings
                ))
        except:
            import sys
            print sys.exc_info()[0]
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
            self.body = '\n\n'.join(itertools.chain(
                self.soup.find(class_="entry").stripped_strings
            ))
        except:
            print "Unable to find score on given page"
