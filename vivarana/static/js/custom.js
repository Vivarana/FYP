$(document).ready(function () {
    $.material.init();

    $("#aplha-slider").noUiSlider({
        start: 0.3,
        connect: "lower",
        step: 0.01,
        range: {
            min: 0,
            max: 1
        }
    });

    $("#curve-slider").noUiSlider({
        start: 0,
        connect: "lower",
        step: 0.01,
        range: {
            min: 0,
            max: 0.25
        }
    });

    $("#bundling-slider").noUiSlider({
        start: 0,
        connect: "lower",
        step: 0.05,
        range: {
            min: 0,
            max: 1
        }
    });

    $(document).on('click', '.yamm .dropdown-menu', function (e) {
        e.stopPropagation()
    });

});