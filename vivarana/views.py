import math
import json
import logging

from pandas import *
from django.http import HttpResponse
from django.shortcuts import render, redirect
from addict import Dict

from helper import file_helper
from helper import aggregate
from rulegen import cart_based_rule_generator as rule_generator
from helper.cluster import *
import vivarana.dataformat.categorize as ct
import vivarana.dataformat.sessionhandle as sh


logger = logging.getLogger(__name__)

original_data_frame = None
current_data_frame = None

pagination_config = {
    "pagination_method": None,
    "page_size": 1000,
    "number_pages": None,
}

properties_map = Dict()


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
    page_number = int(request.GET.get('page', 1)) - 1
    is_last_page = pagination_config["number_pages"] - 1 == page_number
    data_start = page_number * pagination_config["page_size"]
    data_end = (page_number + 1) * pagination_config["page_size"]

    if pagination_config["number_pages"] > 1:
        if is_last_page:
            data_end = len(current_data_frame)
            json_output = (current_data_frame[data_start:]).to_json(orient='records', date_format='iso')
        else:
            json_output = (current_data_frame[data_start:data_end]).to_json(orient='records', date_format='iso')
    else:
        json_output = current_data_frame.to_json(orient='records', date_format='iso')

    if 'Date' not in current_data_frame.columns:
        enable_time_window = False
    else:
        enable_time_window = True

    context = {'columns': column_types, 'result': json_output, 'frame_size': data_end - data_start,
               'enable_time_window': enable_time_window, 'is_last_page': is_last_page,
               'pagination_config': pagination_config, "page_number": page_number + 1, "start_id": data_start}
    return render(request, 'vivarana/visualize.html', context)


def aggregator(request):
    global properties_map
    if not properties_map.WINDOW_TYPE or properties_map.TIME_WINDOW_VALUE == -1 or properties_map.EVENT_WINDOW_VALUE == -1:
        return HttpResponse(ERROR_100)

    if request.method == GET:
        ids = request.GET['selected_ids'][:-1]
        selected_ids = [int(x) for x in ids.split(",")]
        window_type = properties_map.WINDOW_TYPE

        if window_type == TIME_WINDOW:
            new_data_frame = aggregate.aggregate_time_window(int(request.GET['aggregate_func']),
                                                             properties_map.TIME_WINDOW_VALUE,
                                                             properties_map.TIME_GRANULARITY,
                                                             request.GET['attribute_name'], original_data_frame,
                                                             current_data_frame)

        elif window_type == EVENT_WINDOW:
            new_data_frame = aggregate.aggregate_event_window(int(request.GET['aggregate_func']),
                                                              request.GET[ATTRIBUTE_NAME],
                                                              properties_map.EVENT_WINDOW_VALUE, original_data_frame,
                                                              current_data_frame)

        df = new_data_frame.iloc[selected_ids, :]
        json_out = df.to_json(orient='records')
        return HttpResponse(json_out)


def set_window(request):
    global properties_map
    window_type = request.GET[WINDOW_TYPE]
    properties_map.WINDOW_TYPE = window_type
    if window_type == TIME_WINDOW:
        properties_map.TIME_GRANULARITY = request.GET[TIME_GRANULARITY]
        properties_map.TIME_WINDOW_VALUE = int(request.GET[TIME_WINDOW_VALUE])
    if window_type == EVENT_WINDOW:
        properties_map.EVENT_WINDOW_VALUE = int(request.GET[EVENT_WINDOW_VALUE])

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
            pagination_config["pagination_method"] = 'line'
            pagination_config["page_size"] = min([20000, len(current_data_frame)])
            pagination_config["number_pages"] = int(math.ceil(
                len(current_data_frame) / float(pagination_config["page_size"])))
        elif nav_type == 'line':
            page_size = request.POST.get('page-size')
            pagination_config["pagination_method"] = 'line'
            pagination_config["page_size"] = max([1, int(page_size)])
            pagination_config["number_pages"] = int(math.ceil(
                len(current_data_frame) / float(pagination_config["page_size"])))

        if vistype == 'parellel':
            return redirect(VISUALIZE_PATH)
        elif vistype == 'sunburst':
            return redirect(SUNBURST_PATH)
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
        current_data_frame[attribute_name] = original_data_frame[attribute_name]
        df = original_data_frame.iloc[selected_ids, :]
        json_out = df.to_json(orient='records')
        return HttpResponse(json_out)


def sunburst(request):
    return render(request, SUNBURST_PAGE)


def get_tree_data(request):
    if len(current_data_frame.columns) == 2:  # todo get CSV intelligently
        json_tree = ct.build_json_hierarchy(current_data_frame.values)
    else:
        json_tree = ct.build_json_hierarchy_log(sh.get_sessions_data(current_data_frame))
    return HttpResponse(json_tree)


def get_unique_urls(request):
    return HttpResponse(json.dumps(sh.get_unique_urls(current_data_frame)))


def get_session_sequence(request):
    return HttpResponse(sh.get_session_info(current_data_frame))



