$(function() {
    var spec_names = [];
    var sources = [
        function(query, process) {
            if (spec_names.length > 0) {
                process(spec_names);
            } else {
                $.getJSON('/recommendations/get_specification_names/', function(data) {
                    spec_names = data['spec_names'];
                    process(spec_names);
                });
            }
        },
        ["greater than", "less than", "is", "=", ">", "<"],
        []
    ];

    $('form.query-builder').each(function() {
        var $form = $(this);
        $('div.query-build-wrap', this).each(function() {
            var $wrapper = $(this);

            var $grammar_container = $('<span/>');
            $grammar_container.addClass('grammar-container');

            $wrapper.prepend($grammar_container);
            $wrapper.state = 0;

            var $input = $('input', this);
            $input.typeahead({
                'source': sources[0],
                'updater': function(item) {
                    $grammar_container.append('<span class="grammar">' + item + '</span>');

                    $wrapper.state++;
                    this.source = sources[$wrapper.state];
                }
            }).keydown(function(e) {
                if (e.keyCode == 8 && this.value == '' && $wrapper.state > 0) {
                    var new_content = $('span:last-child', $grammar_container).text();
                    $('span:last-child', $grammar_container).remove();
                    $wrapper.state--;
                    $input.data('typeahead').source = sources[$wrapper.state];
                    $input.val(new_content);

                    // Don't continue handling the delete event (so we don't delete the
                    // last character of new_content)
                    return false;
                }
            }).blur(function(e) {
                if ($wrapper.state == 2) {
                    // Build up all the data from all the inputs in the form
                   var data = [];
                    $('div.query-build-wrap', $form).each(function() {
                        var $wrap = $(this);
                        var $grammars = $('span.grammar', $wrap);
                        if ($grammars.length == 2) {
                            data.push([$($grammars[0]).text(), $($grammars[1]).text(), $('input', $wrap).val()]);
                        }
                    });

                    $.get($form.attr('action'), {
                            'query': $('input[name="query"]', $form).val(),
                            'requirements': data
                        }, function() {
                            $.get($form.attr('action'), $form.serialize(), function(data) {
                                console.log(data);
                                $('.results').html(data);
                            });
                        }
                    );
                }
            });
        });
    });

    // Redefine query dumb search
    $('form.redefine-search').each(function() {
        var $form = $(this);
        $('input', this).change(function() {
            $.get($form.attr('action'), $form.serialize(), function(data) {
                console.log(data);
                $('.results').html(data);
            });
        });
    });
});
