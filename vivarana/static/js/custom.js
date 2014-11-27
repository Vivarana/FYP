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
        e.stopPropagation()
    });

    $(function () {
        $("[data-toggle='tooltip']").tooltip();
    });

});


function setTimeWindow() {
//    todo restrict this to numeric values
    var timeGranularity = $("#granularity-select option:selected").text();
    var timeWindowValue = $("#time-window").val();

    $.get('/vivarana/set_time_window/', {time_granularity: timeGranularity, time_window_val: timeWindowValue}, function (data) {
        console.log(data);
    });


}