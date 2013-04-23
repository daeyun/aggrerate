$(function() {
    var $date_span  = $('span.spinner-date');
    var $spinner    = $('input[name="date"]');
    var $categories = $('select[name="category"]');

    var base_date = moment('2000-01-01');

    var convert_int_to_time = (function(month_since_2000) {
        return moment(base_date).add('months', month_since_2000);
    });
    var update_spinner_date = (function($spinner) {
        var ts = convert_int_to_time($spinner.val());
        $date_span.html(ts.format('MMMM YYYY'));
        return ts.format('YYYY-MM-DD');
    });

    var request;
    var load_results = (function(ts, cat) {
        request = $.get('/history/get_results/' + ts + '/', {'c': cat}, function(data) {
            $('.results').html(data);
        });
    });

    var form_updated = (function() {
        load_results(update_spinner_date($spinner), $categories.val());
    });

    $spinner.ready(function() {
        $spinner.val(moment().diff(base_date, 'months'));
        load_results(update_spinner_date($spinner), 'all');
    }).change(form_updated);

    $categories.change(form_updated);
});
