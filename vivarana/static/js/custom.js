$(document).ready(function () {
    $.material.init();

    $("#aplha-slider").noUiSlider({
        start: 0.2,
        connect: "lower",
        range: {
            'min': [0 ],
            '20%': [0.05],
            '50%': [0.1],
            '70%': [0.25],
            '80%': [0.4],
            'max': [0.5]
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


function setTimeWindow() {
    var timeGranularity = $("#granularity-select option:selected").text();
    var timeWindowValue = $("#time-window").val();

    if (isInt(timeWindowValue)) {
        $.get('/set_time_window/', {time_granularity: timeGranularity, time_window_val: timeWindowValue}, function (data) {
            $.snackbar({content: 'Time window has set to ' + timeWindowValue + ' ' + timeGranularity, style: 'toast'});
        });
    } else {
        $.snackbar({content: 'Please specify an integer as the time window value', style: 'toast'});
    }
    return false;

}

function isInt(value) {
    return !isNaN(value) && (function (x) {
        return (x | 0) === x;
    })(parseFloat(value))
}