$(function() {
    var register_comment_delete_handlers = (function($comments) {
        $('.comment-delete-link', $comments).click(function() {
            var $link = $(this);
            $.post('/review/delete_comment/', {
                    'comment_id': parseInt(this.id.substr(1))
                }, function(data) {
                    if (data['deleted']) {
                        $link.parent().remove();
                    }
                }
            );
            return false;
        });
    });

    var load_score = (function($review, review_id) {
        $.getJSON('/review/get_votes/' + review_id + '/', function(data) {
            var score = data['score'];
            s = score + ' vote' + ((score == 1)?'':'s') + ' &middot;';
            $('.votes', $review).html(s);
        });
    });
    var load_review_details = (function($review, review_id) {
        load_score($review, review_id);
        $('.comments', $review).load('/review/get_comments/' + review_id + '/', function() {
            register_comment_delete_handlers(this);
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
        load_review_details($review, review_id);

        // Register handlers
        $('.upvote-link', this).click(link_vote_handler($review, review_id, 1));
        $('.downvote-link', this).click(link_vote_handler($review, review_id, -1));
        $('.novote-link', this).click(link_vote_handler($review, review_id, 0));
        $('.comment-link', this).click(function() {
            $('.comment-form', $review).removeClass('hidden');
            $('.comment-form textarea', $review).focus();
        });

        var $form = $('form', this);
        $form.submit(function() {
            $('.comments', $review).load($form.attr('action'), {
                'review_id': review_id,
                'body_text': $('textarea', $form).val()
            }, function() {
                // Once it's posted, clear the text
                $('textarea', $form).val('');
                $('.comment-form textarea', $review).focus();
                register_comment_delete_handlers($('.comments', $review));
            });

            return false;
        });
    });
});
