var percentageSliderValue = 0.01;

$(document).ready(function () {
    $.material.init();

    // Slider to display depth
    $("#percentage-slider").noUiSlider({
        start: [10],
        step: 10,
        range: {
            'min': [0],
            'max': [100]
        }
    });

    // depth display slider event handler
    $("#percentage-slider").on({'slide': function () {
            percentageSliderValue = $(this).val();
            $("#percentage-opacity-text").text("Maximum Depth to Display: " + percentageSliderValue + " %");

        }, 'change': function () {
            updateData();
        }});

    // event handler for generate rule in nav bar
    $("#sequence-rule-gen").on("click", function () {
        $("#chart2").toggle();
        $("#rulegenerator").toggle();
    });


    $(document).on('click', '.yamm .dropdown-menu', function (e) {
        e.stopPropagation();
    });

    $(function () {
        $("[data-toggle='tooltip']").tooltip();
    });

    // Token field and suggestions
    var engine = new Bloodhound({
        local: $.map(uniqueValues, function (state) {
            return { value: state };
        }),
        datumTokenizer: function (d) {
            return Bloodhound.tokenizers.whitespace(d.value);
        },
        queryTokenizer: Bloodhound.tokenizers.whitespace
    });

    engine.initialize();

    $('#tokenfield-typeahead').tokenfield({
        typeahead: [null, { source: engine.ttAdapter() }]
    });

    // when confirm button was clicked
    $("#ruleconfirm").click(function () {
        alert($('#tokenfield-typeahead').tokenfield('getTokens')[1]["value"]);
    });

    // when close button on rule generator clicked
    $("#close").on("click", function () {
            $("#rulegenerator").toggle();
            $("#chart2").toggle();
            return false;
        }
    );
});

