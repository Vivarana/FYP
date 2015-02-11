import math
import logging
import simplejson
import copy
import ConfigParser

from pandas import *
from django.http import HttpResponse
from django.shortcuts import render, redirect

from helper import file_helper
from helper import aggregate
from rulegen import cart_based_rule_generator as rule_generator
from helper.cluster import *
from vivarana.helper.anomaly import detect_anomalies
from vivarana.helper.pagination import process_pagination
import vivarana.sunburst_visualization.sunburst_views as sun_views
from vivarana.sunburst_visualization.constants import GROUP_BY, COALESCE
from vivarana.helper.state_info import *

logger = logging.getLogger(__name__)

original_data_frame = None
current_data_frame = None

grouping_column = None
grouped_column = None

state_map = {
    WINDOW_TYPE: None,  # p
    TIME_GRANULARITY: None,  # p
    TIME_WINDOW_VALUE: None,  # p
    TIME_WINDOW_ENABLED: False,  # p
    EVENT_WINDOW_VALUE: None,  # p

    DATA_LST: [
        # {
        # CURRENT_ROW_IDS_LST: [],
        # CLUSTER_IDS_DICT: {}, a dict key being row id and value being cluster id
        # CURRENT_PAGE_NUMBER: None
        # }
    ],

    ACTIVE_PAGE_NUMBER: 0,

    PAGINATION_METHOD: None,  # p
    PAGE_SIZE: 1000,  # p
    NUMBER_PAGES: None,  # p

    CLUSTER_COLUMNS_LST: [],
    CLUSTERING_METHOD: None,
    NUMBER_OF_CLUSTERS: None,

    ANOMALY_DETECT_COLUMN: None,

    # stores attribute name as key and (aggregate func, window type, granularity, window size)
    AGGREGATE_FUNCTION_ON_ATTR: {},  # p

    ALL_ATTRIBUTE_LST: [],  # p
    REMOVED_ATTRIBUTE_LST: [],

    BRUSH_MODE: ONE_BRUSH,  # p
    BUNDLING_ENABLED: False,  # p
    CLUSTER_COLORING_ENABLED: False,  # p
    ZSCORE_COLORING_ENABLED: False,  # p
    ALPHA_BLENDING_ENABLED: True,  # p

    BUNDLING_STRENGTH: 0.7,  # p
    CURVE_SMOOTHNESS: 0.2,  # P
    ALPHA_OPACITY: 0.2,  # p

}

initial_state_map = copy.deepcopy(state_map)

aggregate_functions = {
    0: SUM,
    1: AVG,
    2: MIN,
    3: MAX,
    4: COUNT
}


def change_state(request):
    if request.method == POST:
        params = simplejson.loads(request.body, "utf-8")
        state_map[params[PROPERTY_NAME]] = params[PROPERTY_VALUE]
        return HttpResponse('success')


def home(request):
    if request.method == GET:
        return render(request, HOME_PAGE)
    if request.method == POST:
        try:
            input_file = request.FILES[FILE_INPUT]
            with open(TEMP_FILE_PATH, 'wb+') as destination:
                for chunk in input_file.chunks():
                    destination.write(chunk)
            request.session['filename'] = input_file.name.encode('UTF8')
            response_data = parse_file(request)
        except Exception, error:
            logger.error('Error occurred while setting up file.', error)
            response_data['error'] = {'type': 'FILE_ERROR', 'message': 'Error while setting up file. Please try again.'}
            response_data['success'] = False

        return HttpResponse(json.dumps(response_data), content_type="application/json")


def visualize(request):
    if not type(original_data_frame) is pandas.core.frame.DataFrame:
        return redirect(HOME_PATH)
    if 'clusterID' not in current_data_frame.columns:
        current_data_frame['clusterID'] = 0
    column_types = file_helper.get_compatible_column_types(current_data_frame)
    data_start, is_last_page, json_output = process_pagination(state_map, current_data_frame)
    state_map[TIME_WINDOW_ENABLED] = 'Date' in current_data_frame.columns

    context = {'columns': column_types, 'result': json_output, 'is_last_page': is_last_page, "start_id": data_start,
               'state_map': state_map}
    return render(request, 'vivarana/visualize.html', context)


def visualize_next(request):
    direction = request.GET['direction']
    if direction == 'forward':
        if state_map[ACTIVE_PAGE_NUMBER] >= state_map[NUMBER_PAGES] - 1:
            return
        else:
            state_map[ACTIVE_PAGE_NUMBER] += 1
    else:
        if state_map[ACTIVE_PAGE_NUMBER] == 0:
            return
        else:
            state_map[ACTIVE_PAGE_NUMBER] -= 1

    data_start, is_last_page, json_output = process_pagination(state_map, current_data_frame)
    context = {'json_result': json_output, 'is_last_page': is_last_page, "start_id": data_start, 'state_map': state_map}
    json_out = json.dumps(context)
    return HttpResponse(json_out)


def anomaly(request):
    if request.method == GET:
        ids = request.GET['selected_ids'][:-1]
        selected_ids = [int(x) for x in ids.split(",")]
        state_map[ANOMALY_DETECT_COLUMN] = request.GET[ANOMALY_DETECT_COLUMN].encode('UTF8')
        anom_lst = detect_anomalies(state_map, current_data_frame, selected_ids)

        json_response = json.dumps({'anom_lst': anom_lst})
        return HttpResponse(json_response)


def aggregator(request):
    global state_map
    if not state_map[WINDOW_TYPE] or state_map[TIME_WINDOW_VALUE] == -1 \
            or state_map[EVENT_WINDOW_VALUE] == -1:
        return HttpResponse(ERROR_100)

    if request.method == GET:
        ids = request.GET['selected_ids'][:-1]
        selected_ids = [int(x) for x in ids.split(",")]
        window_type = state_map[WINDOW_TYPE]

        aggregate_func = int(request.GET['aggregate_func'])
        attribute_name = request.GET[ATTRIBUTE_NAME]

        aggregated_cols = state_map[AGGREGATE_FUNCTION_ON_ATTR]

        if (attribute_name in aggregated_cols) and aggregated_cols[attribute_name][0] \
                == aggregate_functions[aggregate_func]:
            # if attribute is already aggregated with same function
            df = current_data_frame.iloc[selected_ids, :]
            json_out = df.to_json(orient='records')
            return HttpResponse(json_out)
        else:
            set_aggregate_state(state_map, aggregate_functions[aggregate_func], attribute_name)

            if window_type == TIME_WINDOW:
                new_data_frame = aggregate.aggregate_time_window(aggregate_func,
                                                                 state_map[TIME_WINDOW_VALUE],
                                                                 state_map[TIME_GRANULARITY],
                                                                 attribute_name, original_data_frame,
                                                                 current_data_frame)

            elif window_type == EVENT_WINDOW:
                new_data_frame = aggregate.aggregate_event_window(aggregate_func,
                                                                  attribute_name,
                                                                  state_map[EVENT_WINDOW_VALUE], original_data_frame,
                                                                  current_data_frame)

            df = new_data_frame.iloc[selected_ids, :]
            json_out = df.to_json(orient='records')
            return HttpResponse(json_out)


def set_window(request):
    global state_map
    window_type = request.GET[WINDOW_TYPE]
    state_map[WINDOW_TYPE] = window_type
    if window_type == TIME_WINDOW:
        state_map[TIME_GRANULARITY] = request.GET[TIME_GRANULARITY]
        state_map[TIME_WINDOW_VALUE] = int(request.GET[TIME_WINDOW_VALUE])
        state_map[TIME_WINDOW_ENABLED] = True
    if window_type == EVENT_WINDOW:
        state_map[EVENT_WINDOW_VALUE] = int(request.GET[EVENT_WINDOW_VALUE])
        state_map[TIME_WINDOW_ENABLED] = False

    return HttpResponse('hello world')


def clustering(request):
    if not type(original_data_frame) is pandas.core.frame.DataFrame:
        return redirect(HOME_PATH)

    if request.method == POST:
        params = json.loads(request.body)
        state_map[CLUSTER_COLUMNS_LST] = params['column']
        state_map[CLUSTERING_METHOD] = params[CLUSTERING_METHOD]
        state_map[NUMBER_OF_CLUSTERS] = int(params[NUMBER_OF_CLUSTERS])
        selected_ids = params['selected_ids']
        clustered_dict = apply_clustering(state_map, current_data_frame, selected_ids)
        set_current_data_on_clustering(state_map, selected_ids, clustered_dict)
        json_response = json.dumps(clustered_dict)
        return HttpResponse(json_response)


def preprocessor(request):
    if not type(original_data_frame) is pandas.core.frame.DataFrame:
        return redirect(HOME_PATH)

    if request.method == 'POST':
        vistype = request.POST.get('visualization').encode('UTF8')
        if vistype == PARACOORDS_VIS_TYPE:

            global state_map, current_data_frame

            state_map = copy.deepcopy(initial_state_map)
            current_data_frame = original_data_frame.copy(deep=True)

            columns = request.POST.getlist('column')
            nav_type = request.POST.get('nav-type')
            sampling_type = request.POST.get('sampling-type')

            cols = [original_data_frame.columns[int(i) - 1] for i in columns]
            update_kept_attribute(state_map, cols)
            current_data_frame = file_helper.remove_columns(columns, original_data_frame)
            state_map[ALL_ATTRIBUTE_LST] = list(x.encode('UTF8') for x in current_data_frame.columns)

            # sampling the data
            if sampling_type != 'none':
                if sampling_type == 'random':
                    sample_size = int(request.POST.get('sample-size'))
                    current_data_frame = current_data_frame.loc[
                        np.random.choice(current_data_frame.index, sample_size, replace=False)]

            # pagination
            if nav_type == 'auto':
                state_map[PAGINATION_METHOD] = 'auto'
                state_map[PAGE_SIZE] = min([20000, len(current_data_frame)])
                state_map[NUMBER_PAGES] = int(math.ceil(
                    len(current_data_frame) / float(state_map[PAGE_SIZE])))
            elif nav_type == 'line':
                state_map[PAGINATION_METHOD] = 'line'
                page_size = request.POST.get('page-size')
                state_map[PAGE_SIZE] = 'line'
                state_map[PAGE_SIZE] = max([1, int(page_size)])
                state_map[NUMBER_PAGES] = int(math.ceil(
                    len(current_data_frame) / float(state_map[PAGE_SIZE])))

            return redirect(VISUALIZE_PATH)
        elif vistype == SUNBURST_VIS_TYPE:
            global grouping_column
            global grouped_column
            grouping_column = request.POST.get(GROUPING_COL_NAME).encode('UTF8')
            grouped_column = request.POST.get(GROUPED_COL_NAME).encode('UTF8')
            #create sunburst database
            sun_views.initialize_database(current_data_frame,grouping_column,grouped_column)
            return redirect(
                SUNBURST_PATH + "?" + GROUP_BY + "=" + grouping_column + "&" + COALESCE + "=" + grouped_column)
    else:
        context = file_helper.get_data_summary(original_data_frame)
        context['filename'] = request.session['filename']
        return render(request, PREPROCESSOR_PAGE, context)


def rule_gen(request):
    if request.method == 'POST':
        rule_list = rule_generator.generate(request.body, current_data_frame, state_map)
        json_out = rule_list[8]  # to_json(orient='records')

        json_response = json.dumps({'success': rule_list[0], 'rules': rule_list[1], 'count_selected': rule_list[2],
                                    'count_covered': rule_list[3], 'precision': rule_list[4], 'recall': rule_list[5],
                                    'select_string': rule_list[6], 'window_string': rule_list[7], 'filtered': json_out})
        return HttpResponse(json_response)
    else:
        json_response = "{'message' : done!}"
        return HttpResponse(json_response)


def reset_axis(request):
    if request.method == GET:
        ids = request.GET['selected_ids'][:-1]
        selected_ids = [int(x) for x in ids.split(",")]
        attribute_name = request.GET['attribute_name']
        clear_aggregate_state(state_map, attribute_name)
        current_data_frame[attribute_name] = original_data_frame[attribute_name]
        df = current_data_frame.iloc[selected_ids, :]
        json_out = df.to_json(orient='records')
        return HttpResponse(json_out)


def remove_axis(request):
    if request.method == POST:
        params = simplejson.loads(request.body, "utf-8")
        remove_attribute(params[ATTRIBUTE_NAME], state_map, current_data_frame)
        return HttpResponse('success')


def current_column_lst(request):
    if request.method == GET:
        json_response = json.dumps({'attribute_list': get_current_attribute_list(state_map)})
        return HttpResponse(json_response)


def sunburst(request):
    if not type(original_data_frame) is pandas.core.frame.DataFrame:
        return redirect(HOME_PATH)
    context = {"grouping": grouping_column, "grouped": grouped_column}
    return render(request, SUNBURST_PAGE, context)

def get_max_seq_width(request):
    return HttpResponse(sun_views.get_max_seq_length())

def get_tree_data(request):
    return HttpResponse(sun_views.give_tree_data_structure(current_data_frame,grouped_column))


def get_unique_strings(request):
    return HttpResponse(sun_views.give_unique_coalesce_strings(current_data_frame,grouped_column))


def parse_file(request):
    try:
        response_data = {}
        output = file_helper.handle_uploaded_file(request.session['filename'])
        response_data['success'] = output['success']
        global state_map
        state_map = copy.deepcopy(initial_state_map)
        if output['success']:
            global original_data_frame, current_data_frame
            original_data_frame = output['dataframe']
            original_data_frame.columns = file_helper.get_html_friendly_names(original_data_frame.columns)
            current_data_frame = original_data_frame.copy(deep=True)
            response_data['file_name'] = request.session['filename']
        else:
            response_data['error'] = output['error']
        print response_data
    except Exception, e:
        print e
    return response_data


def apache_log_format(request):
    if request.method == POST:
        params = json.loads(request.body)
        log_format_input = params['format']
        print log_format_input

        config = ConfigParser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), "settings.ini"))
        config.set('parser', 'format', log_format_input)

        try:
            with open(os.path.join(os.path.dirname(__file__), "settings.ini"), 'w') as config_file:
                config.write(config_file)
        except Exception, e:
            json_response = json.dumps({'success': False})
            return HttpResponse(json_response)

        response = parse_file(request)
        json_response = json.dumps(response)
        return HttpResponse(json_response)



#def get_session_sequence(request):
#    return HttpResponse(sun_dp.get_session_info(current_data_frame, grouping_column, grouped_column))



