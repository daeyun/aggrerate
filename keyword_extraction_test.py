import re
import operator

from flask import render_template, request
import flask, time

from aggrerate import app, util
from aggrerate.loginCode import loginCode, flogin
from aggrerate.scraper import ReviewScraper
from aggrerate.scraper.specifications import SpecificationScraper
from flask.ext import login


def extract_keywords():
    (db, cur) = util.get_dict_cursor()
    cur.execute("""
    SELECT
        body_text
    FROM
        reviews
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

    cur.execute("""
    SELECT
        body_text
    FROM
        reviews
    ORDER BY
        id DESC
    LIMIT
        10
    """)
    query_result = cur.fetchall()
    for item in query_result:
        string = item["body_text"]

        tlm = {}
        sn_tlm = {}
        total = 0

        string = item["body_text"]

        words = string.split()

        for word in words:
            total += 1
            if word in tlm:
                tlm[word] += 1
            else:
                tlm[word] = 1

        for word in tlm:
            tlm[word] /= float(total)
            # divide by smoothed background language model
            sn_tlm[word] = tlm[word] / smoothed_blm[word]

        sorted_sn_tlm = sorted(sn_tlm.iteritems(), key=operator.itemgetter(1),
                               reverse=True)

        count = 0

        for pair in sorted_sn_tlm:
            count += 1
            print str(pair[1])[:9], pair[0]
            if count >= 20:
                break

        print ""


extract_keywords()
