var fill = d3.scale.category20();

var draw_tags = (function (words) {
    d3.select("#tagvis").append("svg")
        .attr("width", 470)
        .attr("height", 250)
        .append("g")
        .attr("transform", "translate(235,125)")
        .selectAll("text")
        .data(words)
        .enter().append("text")
        .style("font-size", function(d) { return d.size + "px"; })
        .style("font-family", "Impact")
        .style("fill", function(d, i) { return fill(i); })
        .attr("text-anchor", "middle")
        .attr("transform", function(d) {
            return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
        })
    .text(function(d) { return d.text; });
});

var render_tags = (function(elem) {
    if (elem != undefined) {
        d3.layout.cloud().size([470, 250])
            .words(elem.split(',').map(function(d,index) {
                        return {text: d, size: (2.5-Math.atan(index))*27};
                    }))
            .rotate(function() { return (Math.random()*2-1)*5; })
            .font("Impact")
            .fontSize(function(d) { return d.size; })
            .on("end", draw_tags)
            .start();
    }
});

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

    render_tags($("#tagvis").attr("tags"));
});
