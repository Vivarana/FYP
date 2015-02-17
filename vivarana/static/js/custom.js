$(document).ready(function () {
    $.material.init();

    $(document).on('click', '.yamm .dropdown-menu', function (e) {
        e.stopPropagation();
    });

    $(function () {
        $("[data-toggle='tooltip']").tooltip();
    });

});


function displaySystemState() {
    var modal_body = '<dl class="dl-horizontal">';
    $.getJSON('/get_state_obj/', {}, function (data) {
        if (data['clustering-algo-radios'] !== null) {
            if (data['clustering-algo-radios'] === 'hierarchical-cluster') {
                data['clustering-algo-radios'] = 'Hierarchical Clustering';
            } else if (data['clustering-algo-radios'] === 'kmeans-cluster') {
                data['clustering-algo-radios'] = 'K-modes Clustering';
            } else if (data['clustering-algo-radios'] === 'fuzzy-cluster') {
                data['clustering-algo-radios'] = 'Fuzzy Clustering';
            }

            modal_body += '<dt> Clustering Method Used</dt><dd>' + data['clustering-algo-radios'] + '</dd>';
            modal_body += '<dt> Number of Clusters Specified </dt><dd>' + data['number-of-clusters'] + '</dd>';
            modal_body += '<dt> Attributes used for Clustering</dt><dd>' + data.cluster_columns_lst.join(', ') + '</dd>';
            modal_body += '</br>';
        }

        if (data.time_window_value !== null) {
            modal_body += '<dt> Granularity of Current Time Window </dt><dd>' + data.time_granularity + '</dd>';
            modal_body += '<dt> Size of Current Time Window </dt><dd>' + data.time_window_value + '</dd>';
            modal_body += '</br>';
        } else {
            if (data.event_window_value !== null) {
                modal_body += '<dt> Size of Current Event Window </dt><dd>' + data.event_window_value + '</dd>';
            }
            modal_body += '</br>';
        }
        var agrt_dict = data.aggregate_function_on_attribute;
        if (Object.keys(agrt_dict).length > 0) {
            modal_body += '<table class="table"><thead><tr><th>Attribute Name</th><th>Aggregate Operation</th><th>Window Size</th><th>Window Type</th><th>group_by attribute</th></thead><tbody>';

            for (var key in agrt_dict) {
                if (agrt_dict.hasOwnProperty(key)) {
                    var val = agrt_dict[key];
                    if (val[1] !== 'event') {
                        modal_body += '<tr><td>' + key + '</td><td>' + val[0] + '</td><td>' + val[3] + val[2] + '</td><td>' + val[1] + '</td><td>' + val[4] + '</td>'
                    } else {
                        modal_body += '<tr><td>' + key + '</td><td>' + val[0] + '</td><td>' + val[3] + '</td><td>' + val[1] + '</td><td>' + val[4] + '</td>'
                    }
                }
            }
            modal_body += '</table>';
        }
        if (data.aggregate_group_by_attr !== null) {
            modal_body += '<dt> Attribute used for Group_by Operation </dt><dd>' + data.aggregate_group_by_attr + '</dd>';
        }

        modal_body += '</br>';
        modal_body += '<dt> All Attributes </dt><dd>' + data.all_attribute_lst.join(', ') + '</dd>';

        if (data.removed_attribute_lst.length > 0) {
            modal_body += '<dt> Removed Attributes </dt><dd>' + data.removed_attribute_lst.join(', ') + '</dd>';
        }

        modal_body += '</dl>';
        $("#state_modal_body").html(modal_body);
        $('#state_modal').modal('toggle');
    });

}


function setEventWindow() {
    var isDisabled = $('#event-window').prop('disabled');
    if (isDisabled) {
        return false;
    }
    var eventWindowValue = $("#event-window").val();

    if (isInt(eventWindowValue)) {
        $("#time-window").prop("disabled", true);
        $("#granularity-select").prop("disabled", true);
        $('#set-time-window-btn').addClass('disabled');
        $('#clear-time-window-btn').addClass('disabled');

        $.get('/set_window/', {window_type: 'event', event_window_value: eventWindowValue}, function (data) {
            $.snackbar({content: 'Event window has set to ' + eventWindowValue, style: 'toast'});
            return true;
        });
    } else {
        $.snackbar({content: 'Please specify a positive integer as the event window value', style: 'toast'});
        return false;
    }
    return false;
}

function clearEventWindow() {
    $("#time-window").prop('disabled', false);
    $("#granularity-select").prop("disabled", false);
    $('#set-time-window-btn').removeClass('disabled');
    $('#clear-time-window-btn').removeClass('disabled');

    $.get('/set_window/', {window_type: 'event', event_window_value: -1}, function (data) {
        $("#event-window").val('');
        $.snackbar({content: 'Event window has been cleared', style: 'toast'});
    });
    return true;
}

function clearTimeWindow() {
    $("#event-window").prop('disabled', false);
    $('#set-event-window-btn').removeClass('disabled');
    $('#clear-event-window-btn').removeClass('disabled');

    $.get('/set_window/', {window_type: 'time', time_granularity: 'seconds', time_window_value: -1}, function (data) {
        $("#time-window").val('');
        $.snackbar({content: 'Time window has been cleared', style: 'toast'});
    });
    return true;
}

function setTimeWindow() {
    var isDisabled = $('#time-window').prop('disabled');
    if (isDisabled) {
        return false;
    }

    var timeGranularity = $("#granularity-select option:selected").text();
    var timeWindowValue = $("#time-window").val();

    if (isInt(timeWindowValue)) {
        $("#event-window").prop("disabled", true);
        $('#set-event-window-btn').addClass('disabled');
        $('#clear-event-window-btn').addClass('disabled');

        $.get('/set_window/', {window_type: 'time', time_granularity: timeGranularity, time_window_value: timeWindowValue}, function (data) {
            $.snackbar({content: 'Time window has set to ' + timeWindowValue + ' ' + timeGranularity, style: 'toast'});
        });
    } else {

    }
    return false;

}

function performClustering() {
    var num_of_clusters = $('#num-of-clusters').val();
    if (isInt(num_of_clusters)) {
        $('#cluster_dropdown').removeClass('open');
        var html_string = "<form action='' id='column_select_for_cluster' onsubmit='return false;'>";
        $.getJSON('/current_column_lst/', {}, function (data) {
            var col_list = data.attribute_list;

            for (var i = 0; i < col_list.length; i++) {
                html_string += "<div class='checkbox'><label><input type='checkbox' name='column_for_cluster' value='" +
                    col_list[i] + "' checked> " +
                    "<span class='ripple'></span>" +
                    "<span class='check'>" +
                    "</span>"
                    + col_list[i] + "</label></div>"

            }
            html_string += "</form>";
            $("#cluster_model_body").html(html_string);
            $('#clusterModel').modal('toggle');
            return true;
        });

    } else {
        $.snackbar({content: 'Please specify a positive integer as the number of clusters', style: 'toast'});
        return false;
    }
}

function performRuleGen() {
        var html_string = "<form action='' id='column_select_for_cluster' onsubmit='return false;'>";
        $.getJSON('/current_column_lst/', {}, function (data) {
            var col_list = data.attribute_list;

            for (var i = 0; i < col_list.length; i++) {
                html_string += "<div class='checkbox'><label><input type='checkbox' name='column_for_rulegen' value='" +
                    col_list[i] + "' checked> " +
                    "<span class='ripple'></span>" +
                    "<span class='check'>" +
                    "</span>"
                    + col_list[i] + "</label></div>"

            }
            html_string += "</form>";
            $("#rulegen_model_body").html(html_string);
            $('#myModal').modal('toggle');
            return true;
        });
}


function setAnomalyPeriod() {
    var anomaly_period_size = $("#anomaly_detect_period_size").val();
    var anomaly_granularity = $("#anomaly_detect_granularity option:selected").text();

    if (isInt(anomaly_period_size)) {
        $.post("/change_state/", JSON.stringify({property_name: "anomaly_detect_period_size", property_value: anomaly_period_size}), function (data) {
        });
        $.post("/change_state/", JSON.stringify({property_name: "anomaly_detect_granularity", property_value: anomaly_granularity}), function (data) {
        });

        $.snackbar({content: 'Anomaly Detection period size has been set to ' + anomaly_period_size + ' ' + anomaly_granularity, style: 'toast'});
        return true
    } else {
        $.snackbar({content: 'Please specify a positive integer as the period size', style: 'toast'});
        return false;
    }
}

function setMaxAnomaly() {
    var anomaly_max_size = $("#anomaly_detect_max_size").val();
    if ((anomaly_max_size > 0) && (anomaly_max_size < 100)) {
        $.post("/change_state/", JSON.stringify({property_name: "anomaly_detect_max_size", property_value: anomaly_max_size}), function (data) {
        });
        $.snackbar({content: 'Maximum size of anomalies which should be detected has been set to ' + anomaly_max_size + '% of data ', style: 'toast'});
        return true
    } else {
        $.snackbar({content: 'Maximum size of Anomalies detected should be a percentage value', style: 'toast'});
        return false;
    }
}

function isInt(value) {
    return !isNaN(value) && (function (x) {
        return ((x | 0) === x) && x > 0;
    })(parseFloat(value))
}