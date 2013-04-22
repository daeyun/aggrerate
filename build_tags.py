import re
import operator
import flask
import time
from aggrerate import app, util
from aggrerate.loginCode import loginCode, flogin
from aggrerate.scraper import ReviewScraper
from aggrerate.scraper.specifications import SpecificationScraper
from flask import render_template, request
from flask.ext import login


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    return False


def extract_keywords():
    (db, cur) = util.get_dict_cursor()
    cur.execute("""
    SELECT
        reviews.body_text
    FROM
        reviews
    INNER JOIN
        scraped_reviews
    ON
        reviews.id = scraped_reviews.review_id
    ORDER BY
        reviews.date DESC
    """)

    blm = {}
    smoothed_blm = {}
    total = 0

    query_result = cur.fetchall()
    for item in query_result:
        string = item["body_text"]

        words = string.split()

        for word in words:
            total += 1
            if word in blm:
                blm[word] += 1
            else:
                blm[word] = 1

    for word in blm:
        smoothed_blm[word] = (blm[word]+1) / float(total+20000)

    product_ids = []

    cur.execute("""
    SELECT
        DISTINCT reviews.product_id
    FROM
        reviews
    INNER JOIN
        scraped_reviews
    ON
        reviews.id = scraped_reviews.review_id
    ORDER BY
        reviews.product_id ASC
    """)
    query_result = cur.fetchall()
    for item in query_result:
        product_ids.append(item["product_id"])

    for product_id in product_ids:
        tlm = {}
        sn_tlm = {}
        total = 0

        cur.execute("""
        SELECT
            reviews.body_text, reviews.product_id
        FROM
            reviews
        INNER JOIN
            scraped_reviews
        ON
            reviews.id = scraped_reviews.review_id
        WHERE
            reviews.product_id = %s
        """, product_id)
        query_result = cur.fetchall()
        for item in query_result:
            string = item["body_text"]
            words = string.split()

            for word in words:
                total += 1
                if word in tlm:
                    tlm[word] += 1
                else:
                    tlm[word] = 1

        for word in tlm:
            tlm[word] = max(tlm[word], 0) / float(total)
            # divide by smoothed background language model
            sn_tlm[word] = tlm[word] / smoothed_blm[word]

        sorted_sn_tlm = sorted(sn_tlm.iteritems(), key=operator.itemgetter(1),
                               reverse=True)

        count = 0

        print product_id

        tags = []

        for pair in sorted_sn_tlm:
            if len(pair[0]) == 1 or is_number(pair[0]) or "cnet" in pair[0] or\
               "verge" in pair[0] or "mags" in pair[0] or "wired" in pair[0]:
                    continue
            count += 1
            print str(pair[1])[:9], pair[0]
            tags.append(pair[0])
            if count >= 40:
                break

        stringified_tags = ",".join(tags)
        print stringified_tags

        print ""

        cur.execute("""
        INSERT INTO product_tags VALUES (NULL, %s, %s)
        ON DUPLICATE KEY UPDATE product_id = %s, tags = %s;
        """, (product_id, stringified_tags, product_id, stringified_tags))
        db.commit()

extract_keywords()
