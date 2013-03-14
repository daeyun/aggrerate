import sys

from aggrerate.scraper import ReviewScraper
from aggrerate.scraper.specifications import SpecificationScraper

def test_review_scraper():
    urls = [
        "http://www.theverge.com/2012/11/2/3589280/google-nexus-4-review",
        "http://reviews.cnet.com/samsung-galaxy-s3-review/",
        "http://gdgt.com/apple/iphone/5/",
        "http://www.pcmag.com/article2/0,2817,2410419,00.asp",
        "http://www.wired.com/reviews/2013/02/google-chromebook-pixel/"
    ]

    for url in urls:
        scraper = ReviewScraper.from_url(url)
        if scraper:
            scraper.parse_page()
            print scraper
        else:
            print "Couldn't find scraper :("

def test_specifications_scraper():
    s = SpecificationScraper("http://www.theverge.com/products/roku-3/6920")
    s.download_page()
    s.parse_page()

if __name__ == '__main__':
    if 'reviews' in sys.argv:
        test_review_scraper()
    if 'specs' in sys.argv:
        test_specifications_scraper()
