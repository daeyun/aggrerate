delimiter //
CREATE FUNCTION metascore(uid int(11), pid int(11))
RETURNS decimal(9, 1)
BEGIN
    DECLARE sum_scores decimal(9, 1);
    DECLARE sum_basic_scores decimal(9, 1);
    DECLARE num_scores decimal(9, 1);

    SELECT
            SUM(COALESCE(user_preferences.priority, 1.0)), SUM(reviews.score*COALESCE(user_preferences.priority, 1.0))
        INTO
            @num_scores, @sum_scores
    FROM
    scraped_reviews
    INNER JOIN reviews
        ON (scraped_reviews.review_id = reviews.id) AND (reviews.product_id = pid)
    LEFT JOIN
        user_preferences
        ON (scraped_reviews.review_source_id = user_preferences.review_sources_id) AND (user_preferences.user_id = uid);

    RETURN @sum_scores/@num_scores;
END//
delimiter ;

