from aggrerate.scraper import ReviewScraper, register_scraper

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
