var percentageSliderValue = 5;

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
        step: 5,
        range: {
            'min': [0],
            'max': [100]
        }
    });

    $("#percentage-slider").on({'slide': function () {
        percentageSliderValue = $(this).val();
        $("#percentage-opacity-text").text("Maximum Depth to Display: " + percentageSliderValue );

    }, 'change': function () {
        updateData();
    }});


    $("#exampleModal").draggable({
        handle: ".modal-header"
    });

    // toggle generate rule navbar

    $("#sequence-rule-gen").on("click", function () {
        $("#chart2").toggle();
        $("#rulegenerator").toggle();
    });

    //suggestion token field

    var colorsand = ['red','green','white','blue'];

$("#ruleconfirm").click(function() {
    alert($('#rule-input').tokenfield('getTokens')[1]["value"]);
});

    $("#close").on("click", function () {
            $("#rulegenerator").toggle();
            $("#chart2").toggle();
            return false;
        }
    );


});

