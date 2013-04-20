$(function() {
    var sources = [
        function(query, process) {
            return ["Hello", "World"];
        },
        ["greater than", "less than", "is", "="],
        ["Hello", "World"]
    ];

    $('form.query-builder').each(function() {
        var $form = $(this);
        $('div.query-build-wrap', this).each(function() {
            var $wrapper = $(this);

            var $grammar_container = $('<span/>');
            $grammar_container.addClass('grammar-container');

            $wrapper.prepend($grammar_container);

            $('input', this).typeahead({
                'source': sources[0],
                'updater': function(item) {
                    console.log(this);
                    console.log(item);
                    $grammar_container.append('<span class="grammar">' + item + '</span>');

                    if (this.state) {
                        this.state++;
                    } else {
                        this.state = 1;
                    }

                    this.source = sources[this.state];
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
