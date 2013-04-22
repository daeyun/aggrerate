$(function() {
    var $date_span = $('span.spinner-date');
    var $spinner   = $('input[name="date"]');

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
    var load_results = (function(ts) {
        request = $.get('/history/get_results/' + ts + '/', function(data) {
            $('.results').html(data);
        });
    });

    $spinner.ready(function() {
        var months = moment().diff(base_date, 'months');
        $spinner.val(months);
        load_results(update_spinner_date($spinner));
    }).change(function(value) {
        load_results(update_spinner_date($spinner));
    });
});
