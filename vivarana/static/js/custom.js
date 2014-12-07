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

function setEventWindow() {
    var isDisabled = $('#event-window').prop('disabled');
    if (isDisabled) {
        console.log("event window disabled");
        return false;
    }
    var eventWindowValue = $("#event-window").val();
    $("#time-window").prop("disabled", true);
    $("#granularity-select").prop("disabled", true);

    if (isInt(eventWindowValue)) {
        $.get('/set_window/', {window_type: 'event', event_window_value: eventWindowValue}, function (data) {
            $.snackbar({content: 'Event window has set to ' + eventWindowValue, style: 'toast'});
        });
    } else {
        $.snackbar({content: 'Please specify a positive integer as the event window value', style: 'toast'});
    }
    return false;
}

function clearEventWindow() {
    $("#time-window").prop('disabled', false);
    $("#granularity-select").prop("disabled", false);
    $.get('/set_window/', {window_type: 'event', event_window_value: 0}, function (data) {
        $.snackbar({content: 'Event window has been cleared', style: 'toast'});
    });
    return true;
}

function clearTimeWindow() {
    $("#event-window").prop('disabled', false);
    $.get('/set_window/', {window_type: 'time', time_granularity: 'seconds', time_window_value: 0}, function (data) {
        $.snackbar({content: 'Time window has been cleared', style: 'toast'});
    });
    return true;
}

function setTimeWindow() {
    var isDisabled = $('#time-window').prop('disabled');
    if (isDisabled) {
        console.log("time window disabled");
        return false;
    }
    $("#event-window").prop("disabled", true);

    var timeGranularity = $("#granularity-select option:selected").text();
    var timeWindowValue = $("#time-window").val();

    if (isInt(timeWindowValue)) {
        $.get('/set_window/', {window_type: 'time', time_granularity: timeGranularity, time_window_value: timeWindowValue}, function (data) {
            $.snackbar({content: 'Time window has set to ' + timeWindowValue + ' ' + timeGranularity, style: 'toast'});
        });
    } else {
        $.snackbar({content: 'Please specify a positive integer as the time window value', style: 'toast'});
    }
    return false;

}

function isInt(value) {
    return !isNaN(value) && (function (x) {
        return ((x | 0) === x) && x > 0;
    })(parseFloat(value))
}