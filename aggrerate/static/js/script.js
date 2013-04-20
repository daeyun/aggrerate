// Wait for the document to be ready
$(function() {
    $('.pretty-date').text(function(index, text) {
        return moment(text).calendar();
    });
    $('#message').delay(2000).slideUp(900);

    // Turn a number into stars
    // Source: http://stackoverflow.com/questions/1987524/
    $('span.stars').each(function() {
        var val = parseFloat($(this).html()) / 2.0;
        var size = Math.max(0, (Math.min(5, val))) * 16;
        var $span = $('<span />').width(size);
        $(this).html($span);
    });

    // Auto-submit user preferences
    $('form.source-preferences-form').each(function() {
        var $form = $(this);
        $('input[name=priority]', this).change(function() {
            $.post($form.attr('action'), $form.serialize());
        });
    });
});
