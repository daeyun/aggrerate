import re
import operator

from flask import render_template, request
import flask, time

from aggrerate import app, util
from aggrerate.loginCode import loginCode, flogin
from aggrerate.scraper import ReviewScraper
from aggrerate.scraper.specifications import SpecificationScraper
from flask.ext import login


def update_scraped_reviews():

    (db, cur) = util.get_dict_cursor()
    cur.execute("""
    SELECT
        r.id, sr.id, sr.review_source_id, sr.url
    FROM
        reviews r
    INNER JOIN scraped_reviews sr
    ON r.id = sr.review_id
    """)

    query_result = cur.fetchall()

    for result in query_result:

        scraper = ReviewScraper.from_url(result["url"])
        scraper.parse_page()

        reviewId = result["id"]
        scrapedReviewId = result["sr.id"]

        print "Updating %s" % result
        print "Score: %s, Words in body text: %s, New Date: %s" % \
            (scraper.score, len(scraper.body.split()), scraper.timestamp)

        cur.execute("""
        UPDATE
            reviews
        SET
            score = %s,
            body_text = %s,
            date = %s
        WHERE
            reviews.id = %s
        """, (scraper.score, scraper.body, scraper.timestamp, reviewId)
        )

        cur.execute("""
        UPDATE
            scraped_reviews
        SET
            blurb = %s
        WHERE
            id = %s
        """, (scraper.blurb, scrapedReviewId)
        )

        db.commit()



update_scraped_reviews()
