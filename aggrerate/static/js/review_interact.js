$(function() {
    var load_score = (function($review, review_id) {
        $.getJSON('/review/get_votes/' + review_id + '/', function(data) {
            var score = data['score'];
            s = score + ' vote' + ((score == 1)?'':'s') + ' &middot;';
            $('.votes', $review).html(s);
        });
    });

    var submit_vote = (function($review, review_id, value) {
        $.post('/review/submit_vote/', {'review_id': review_id, 'value': value}, function(data) {
            load_score($review, review_id);
        });
    });

    var link_vote_handler = (function($review, review_id, score) {
        return (function() {
            submit_vote($review, review_id, score);
            return false;
        });
    });

    $('.review').each(function() {
        var $review = $(this);

        // On load, we need to load the base vote values 
        var review_id = parseInt(this.id.substr(1));
        load_score($review, review_id);

        // Register upvote/downvote handlers
        $('.upvote-link', this).click(link_vote_handler($review, review_id, 1));
        $('.downvote-link', this).click(link_vote_handler($review, review_id, -1));
        $('.novote-link', this).click(link_vote_handler($review, review_id, 0));
    });
});
