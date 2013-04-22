delimiter //
DROP FUNCTION IF EXISTS metascore_with_date//
CREATE FUNCTION metascore_with_date(uid int(11), pid int(11), dt datetime)
RETURNS decimal(9, 1)
BEGIN
    DECLARE sum_scores decimal(9, 1);
    DECLARE sum_basic_scores decimal(9, 1);
    DECLARE num_scores decimal(9, 1);

    SELECT
        SUM(COALESCE(user_preferences.priority, 1.0)), SUM(GREATEST(0, reviews.score*COALESCE(user_preferences.priority, 1.0)-ATAN(TIMESTAMPDIFF(MONTH, reviews.date, dt)/40-1)-0.8))
    INTO
        @num_scores, @sum_scores
    FROM
        scraped_reviews
    INNER JOIN reviews
        ON (scraped_reviews.review_id = reviews.id) AND (reviews.product_id = pid)
    LEFT JOIN user_preferences
        ON (scraped_reviews.review_source_id = user_preferences.review_sources_id) AND (user_preferences.user_id = uid)
    WHERE
        reviews.date <= dt;

    RETURN IFNULL(@sum_scores/@num_scores, 0);
END//
delimiter ;

