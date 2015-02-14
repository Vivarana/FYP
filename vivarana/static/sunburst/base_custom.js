var percentageSliderValue = 0.01;

$(document).ready(function () {
    $.material.init();
    /*  $(document).on('click', '.yamm .dropdown-menu', function (e) {
     e.stopPropagation();
     });*/

    // show tooltips

    $("[data-toggle='tooltip']").tooltip();
    // Percentage Slider
    $("#percentage-slider").noUiSlider({
        start: [10],
        step: 10,
        range: {
            'min': [0],
            'max': [100]
        }
    });

    $("#percentage-slider").on({'slide': function () {
        percentageSliderValue = $(this).val();
        $("#percentage-opacity-text").text("Maximum Depth to Display: " + percentageSliderValue + " %");

    }, 'change': function () {
        updateData();
    }});
    //Filter model
    $('#filter-input').tokenfield({
        autocomplete: {
            source: colors,
            delay: 100
        },
        showAutocompleteOnFocus: true
    });

    $("#exampleModal").draggable({
        handle: ".modal-header"
    });

    // toggle generate rule navbar

    $("#sequence-rule-gen").on("click", function () {
        $("#chart2").toggle();
        $("#rulegenerator").toggle();
    });

    //suggestion token field
    var engine = new Bloodhound({
        local: $.map(colors, function (state) {
            return { value: state };
        }),
        datumTokenizer: function (d) {
            return Bloodhound.tokenizers.whitespace(d.value);
        },
        queryTokenizer: Bloodhound.tokenizers.whitespace
    });

    engine.initialize();


    // rule generate panel
    $('#rule-input').typeahead({
  hint: true,
  highlight: true,
  minLength: 1
},
{
  name: 'engine',
  displayKey: 'value',
  // `ttAdapter` wraps the suggestion engine in an adapter that
  // is compatible with the typeahead jQuery plugin
  source: engine.ttAdapter()
});

    $("#ruleconfirm").click(function () {
        alert($('#tokenfield-typeahead').tokenfield('getTokens')[1]["value"]);
    });

    $("#close").on("click", function () {
            $("#rulegenerator").toggle();
            $("#chart2").toggle();
            return false;
        }
    );


});

