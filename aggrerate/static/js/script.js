// Wait for the document to be ready
$(function() {
    $('.pretty-date').text(function(index, text) {
        return moment(text).calendar();
    });
});
