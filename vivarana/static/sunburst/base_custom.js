var percentageSliderValue = 0.01;

$(document).ready(function () {
    $.material.init();
    $("#percentage-slider").noUiSlider({
        start: [ 0.1 ],
        connect: "lower",
        step: 0.01,
	range: {
        'min': [0 ],
            '20%': [0.5],
            '50%': [1],
            '70%': [5],
            '90%': [10],
            'max': [20]
    }
    });

    $("#curve-slider").noUiSlider({
        start: 0.2,
        connect: "lower",
        step: 0.01,
        range: {
            min: 0,
            max: 0.25
        }
    });

    $("#bundling-slider").noUiSlider({
        start: 0.7,
        connect: "lower",
        step: 0.05,
        range: {
            min: 0,
            max: 1
        }
    });

    $(document).on('click', '.yamm .dropdown-menu', function (e) {
        e.stopPropagation();
    });

    $(function () {
        $("[data-toggle='tooltip']").tooltip();
    });


});

