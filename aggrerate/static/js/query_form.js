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

        var ajax_submit = (function() {
            // Build up all the data from all the inputs in the form
           var data = [];
            $('div.query-build-wrap.success', $form).each(function() {
                var $wrap = $(this);
                var $grammars = $('span.grammar', $wrap);
                if ($grammars.length == 2) {
                    data.push([$($grammars[0]).text(), $($grammars[1]).text(), $('input', $wrap).val()]);
                }
            });

            var request_data = {
                'query': $('input[name="query"]', $form).val(),
                'requirements': data,
                'num_requirements': data.length
            }

            $.get($form.attr('action'), request_data, function(data) {
                $('.results').html(data);
            });
        });

        $('input', this).each(function() {
            $(this).change(function() {
                ajax_submit();
            });
        });

        var init_query_wrap = (function($wrapper) {
            var $grammar_container = $('<span/>');
            $grammar_container.addClass('grammar-container');

            $wrapper.prepend($grammar_container);
            $wrapper.state = 0;

            var $input = $('input', $wrapper);
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
            }).keyup(function(e) {
                if ($wrapper.state == 2 && $input.val().length > 0) {
                    $wrapper.addClass('success');
                } else {
                    $wrapper.removeClass('success');
                }

                // Optionally add a new query-build field
                if ($('div.query-build-wrap').length == $('div.query-build-wrap.success').length) {
                    add_query_wrap();
                }
            }).blur(function(e) {
                if ($wrapper.state == 2) {
                    ajax_submit();
                } else if ($wrapper.state == 0 && $input.val() == '' && !$wrapper.is(':last-child')) {
                    $wrapper.remove();
                    ajax_submit();
                }
            });
        });

        var $query_build_container = $('div.query-build-container', this);
        var add_query_wrap = (function() {
            $wrapper = $('<div class="query-build-wrap control-group"><div class="query-input-parent"><input type="text" autocomplete="false"></div></div>');
            $query_build_container.append($wrapper);
            init_query_wrap($wrapper);
        });

        // Add the first field
        add_query_wrap();

        // Load some data by default
        ajax_submit();
    });
});
