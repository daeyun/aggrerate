from bs4 import BeautifulSoup
import urllib2

class SpecificationScraper(object):
    def __init__(self, url):
        self.url = url
        self.specs_soup = None
        self.specs = {}

    def download_page(self):
        if self.specs_soup is not None:
            return

        try:
            p = urllib2.urlopen(self.url, None)
            s = BeautifulSoup(p.read(), "html.parser")

            self.specs_soup = s.find(id="product-specs")
        except:
            print "Failed to download specs"

    def parse_page(self):
        self.download_page()
        try:
            for tr in self.specs_soup.find_all('tr'):
                ths = tr.find_all('th')
                self.specs[ths[0].text] = ths[1].text
        except:
            print "Unable to parse specs"
