import math
import json
import logging
import simplejson

from pandas import *
from django.http import HttpResponse
from django.shortcuts import render, redirect

from helper import file_helper
from helper import aggregate
from rulegen import cart_based_rule_generator as rule_generator
from helper.cluster import *
import vivarana.sunburst_visualization.json_parser as ct
import vivarana.sunburst_visualization.data_processor as sh
from vivarana.sunburst_visualization.constants import GROUP_BY, COALESCE
from vivarana.helper.state_info import *

logger = logging.getLogger(__name__)

original_data_frame = None
current_data_frame = None

grouping_column = None
grouped_column = None

pagination_config = {
    "pagination_method": None,
    "page_size": 1000,
    "number_pages": None,
    "current_page_number": 1
}

state_map = {
    WINDOW_TYPE: None,
    TIME_GRANULARITY: None,
    TIME_WINDOW_VALUE: None,
    TIME_WINDOW_ENABLED: False,
    EVENT_WINDOW_VALUE: None,

    DATA_LST: [
        # {
        # CURRENT_ROW_IDS_LST: [],
        # CURRENT_COLUMNS_LST: [],
        # CLUSTER_IDS_LST: [],
        # CURRENT_PAGE_NUMBER: None
        # }
    ],

    PAGINATION_METHOD: None,
    PAGE_SIZE: 1000,
    NUMBER_PAGES: None,

    CLUSTER_COLUMNS_LST: [],
    CLUSTERING_METHOD: None,
    NUMBER_OF_CLUSTERS: None,

    # stores attribute name as key and (aggregate func, window type, granularity, window size)
    AGGREGATE_FUNCTION_ON_ATTR: {},  # p
    REMOVED_ATTRIBUTES: [],

    BRUSH_MODE: ONE_BRUSH,  # p
    BUNDLING_ENABLED: False,  # p
    CLUSTER_COLORING_ENABLED: False,  # p
    ZSCORE_COLORING_ENABLED: False,  # p
    ALPHA_BLENDING_ENABLED: True,  # p

    BUNDLING_STRENGTH: 0.7,  # p
    CURVE_SMOOTHNESS: 0.2,  # P
    ALPHA_OPACITY: 0.2,  # p

}

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
        print params[PROPERTY_NAME], state_map[params[PROPERTY_NAME]]
        return HttpResponse('success')


def home(request):
    if request.method == GET:
        return render(request, HOME_PAGE)

    if request.method == POST:
        response_data = {}
        try:
            input_file = request.FILES[FILE_INPUT]
            output = file_helper.handle_uploaded_file(input_file)
            response_data['success'] = output['success']
            if output['success']:
                global original_data_frame, current_data_frame
                original_data_frame = output['dataframe']
                original_data_frame.columns = file_helper.get_html_friendly_names(original_data_frame.columns)
                current_data_frame = original_data_frame.copy(deep=True)
                request.session['filename'] = input_file.name.encode('UTF8')
                response_data['file_name'] = input_file.name.encode('UTF8')
            else:
                response_data['error'] = output['error']

        except Exception, error:
            logger.error('Error occurred while setting up file.', error)
            response_data['error'] = "Error while setting up file. Please try again."
            response_data['success'] = False

        return HttpResponse(json.dumps(response_data), content_type="application/json")


def visualize(request):
    if not type(original_data_frame) is pandas.core.frame.DataFrame:
        return redirect(HOME_PATH)
    current_data_frame['clusterID'] = 0
    column_types = file_helper.get_compatible_column_types(current_data_frame)

    # minus one to convert zero based to one based
    set_current_page_no(state_map, 0)
    # todo set current row_ids, try to set whole DATA_LST at once
    page_number = get_current_page_no(state_map)
    is_last_page = state_map[NUMBER_PAGES] - 1 == page_number
    data_start = page_number * state_map[PAGE_SIZE]
    data_end = (page_number + 1) * state_map[PAGE_SIZE]

    if state_map[NUMBER_PAGES] > 1:
        json_output = (current_data_frame[data_start:data_end]).to_json(orient='records', date_format='iso')
    else:
        json_output = current_data_frame.to_json(orient='records', date_format='iso')

    if 'Date' not in current_data_frame.columns:
        enable_time_window = False
    else:
        enable_time_window = True

    context = {'columns': column_types, 'result': json_output, 'frame_size': data_end - data_start,
               'enable_time_window': enable_time_window, 'is_last_page': is_last_page,
               "page_number": page_number + 1, "start_id": data_start,
               'state_map': state_map}
    return render(request, 'vivarana/visualize.html', context)


def visualize_next(request):
    if get_current_page_no(state_map) == state_map[NUMBER_PAGES]:
        return
    direction = request.GET['direction']
    if direction == 'forward':
        increment_current_page_no(state_map)
    else:
        decrement_current_page_no(state_map)

    page_number = get_current_page_no(state_map)
    print page_number
    is_last_page = state_map[NUMBER_PAGES] - 1 == page_number
    data_start = page_number * state_map[PAGE_SIZE]
    data_end = (page_number + 1) * state_map[PAGE_SIZE]

    if state_map[NUMBER_PAGES] > 1:
        if is_last_page:
            json_output = (current_data_frame[data_start:]).to_json(orient='records', date_format='iso')
        else:
            json_output = (current_data_frame[data_start:data_end]).to_json(orient='records', date_format='iso')
    else:
        json_output = current_data_frame.to_json(orient='records', date_format='iso')

    context = {'json_result': json_output, 'is_last_page': is_last_page,
               "page_number": page_number + 1, "start_id": data_start}
    json_out = json.dumps(context)
    return HttpResponse(json_out)


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
    if window_type == EVENT_WINDOW:
        state_map[EVENT_WINDOW_VALUE] = int(request.GET[EVENT_WINDOW_VALUE])

    return HttpResponse('hello world')


def clustering(request):
    if not type(original_data_frame) is pandas.core.frame.DataFrame:
        return redirect(HOME_PATH)

    if request.method == POST:
        params = json.loads(request.body)
        columns = params['column']
        cluster_method = params[CLUSTERING_METHOD]
        number_of_clusters = int(params[NUMBER_OF_CLUSTERS])
        selected_ids = params['selected_ids']
        clustered_dict = apply_clustering(cluster_method, number_of_clusters, original_data_frame, selected_ids,
                                          columns)
        json_response = json.dumps(clustered_dict)
        return HttpResponse(json_response)


def preprocessor(request):
    if not type(original_data_frame) is pandas.core.frame.DataFrame:
        return redirect(HOME_PATH)

    if request.method == 'POST':
        columns = request.POST.getlist('column')
        nav_type = request.POST.get('nav-type')
        sampling_type = request.POST.get('sampling-type')
        vistype = request.POST.get('visualization')

        global current_data_frame
        current_data_frame = file_helper.remove_columns(columns, original_data_frame)

        # sampling the data
        if sampling_type != 'none':
            if sampling_type == 'random':
                sample_size = int(request.POST.get('sample-size'))
                print len(current_data_frame.index), sample_size
                current_data_frame = current_data_frame.loc[
                    np.random.choice(current_data_frame.index, sample_size, replace=False)]

        # pagination
        if nav_type == 'auto':
            state_map[PAGINATION_METHOD] = 'line'
            state_map[PAGE_SIZE] = min([20000, len(current_data_frame)])
            state_map[NUMBER_PAGES] = int(math.ceil(
                len(current_data_frame) / float(state_map[PAGE_SIZE])))
        elif nav_type == 'line':
            page_size = request.POST.get('page-size')
            state_map[PAGE_SIZE] = 'line'
            state_map[PAGE_SIZE] = max([1, int(page_size)])
            state_map[NUMBER_PAGES] = int(math.ceil(
                len(current_data_frame) / float(state_map[PAGE_SIZE])))

        if vistype == PARACOORDS_VIS_TYPE:
            return redirect(VISUALIZE_PATH)
        elif vistype == SUNBURST_VIS_TYPE:
            global grouping_column
            global grouped_column
            grouping_column = request.POST.get(GROUPING_COL_NAME)
            grouped_column = request.POST.get(GROUPED_COL_NAME)
            # delete after testing
            grouping_column = 'Remote_host'
            grouped_column = 'URL'
            return redirect(
                SUNBURST_PATH + "?" + GROUP_BY + "=" + grouping_column + "&" + COALESCE + "=" + grouped_column)
        return redirect(VISUALIZE_PATH)
    else:
        context = file_helper.get_data_summary(original_data_frame)
        context['filename'] = request.session['filename']
        return render(request, PREPROCESSOR_PAGE, context)


def rule_gen(request):
    if request.method == 'POST':
        rule_list = rule_generator.generate(request.body, current_data_frame)
        json_response = json.dumps({'rules': rule_list})
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
        df = original_data_frame.iloc[selected_ids, :]
        json_out = df.to_json(orient='records')
        return HttpResponse(json_out)


def sunburst(request):
    context = {"grouping": grouping_column, "grouped": grouped_column}

    return render(request, SUNBURST_PAGE, context)


def get_tree_data(request):
    if len(current_data_frame.columns) == 2:  # todo get CSV intelligently
        json_tree = ct.build_json_hierarchy(current_data_frame.values)
    else:
        json_tree = ct.build_json_hierarchy_log(
            sh.get_sessions_data(current_data_frame, grouping_column, grouped_column))
    return HttpResponse(json_tree)


def get_unique_urls(request):
    return HttpResponse(json.dumps(sh.get_unique_urls(current_data_frame, grouped_column)))


def get_session_sequence(request):
    return HttpResponse(sh.get_session_info(current_data_frame, grouping_column, grouped_column))



