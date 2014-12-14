from pandas import *
from pandas.io import json
from django.http import HttpResponse
from django.shortcuts import render, redirect
import logging
import json

from helper import file_helper
from helper import aggregate
from rulegen import cart_based_rule_generator as rule_generator
from helper.cluster import *
import vivarana.dataformat.categorize as ct


original_data_frame = None
current_data_frame = None

properties_map = {}

logger = logging.getLogger('root')


def home(request):
    context = {}
    return render(request, 'vivarana/home.html', context)


def visualize(request):
    if not type(original_data_frame) is pandas.core.frame.DataFrame:
        return redirect(UPLOAD_PATH)
    column_types = file_helper.get_compatible_column_types(current_data_frame)
    json_output = current_data_frame.to_json(orient='records', date_format='iso')
    if 'Date' not in current_data_frame.columns:
        enable_time_window = False
    else:
        enable_time_window = True
    context = {'columns': column_types, 'result': json_output, 'frame_size': len(current_data_frame),
               'enable_time_window': enable_time_window}
    return render(request, 'vivarana/visualize.html', context)


def aggregator(request):
    if WINDOW_TYPE not in properties_map:
        return HttpResponse('error')

    if request.method == GET:
        ids = request.GET['selected_ids'][:-1]
        selected_ids = [int(x) for x in ids.split(",")]
        window_type = properties_map[WINDOW_TYPE]

        if window_type == TIME_WINDOW:
            new_data_frame = aggregate.aggregate_time_window(int(request.GET['aggregate_func']),
                                                             properties_map['time_window_value'],
                                                             properties_map['time_granularity'],
                                                             request.GET['attribute_name'], original_data_frame,
                                                             current_data_frame)

        elif window_type == EVENT_WINDOW:
            new_data_frame = aggregate.aggregate_event_window(int(request.GET['aggregate_func']),
                                                              request.GET[ATTRIBUTE_NAME],
                                                              properties_map[EVENT_WINDOW_VALUE], original_data_frame,
                                                              current_data_frame)

        df = new_data_frame.iloc[selected_ids, :]
        json_out = df.to_json(orient='records')
        return HttpResponse(json_out)


def set_window(request):
    window_type = request.GET[WINDOW_TYPE]
    properties_map[WINDOW_TYPE] = window_type
    if window_type == TIME_WINDOW:
        properties_map[TIME_GRANULARITY] = request.GET[TIME_GRANULARITY]
        properties_map[TIME_WINDOW_VALUE] = int(request.GET[TIME_WINDOW_VALUE])
    if window_type == EVENT_WINDOW:
        properties_map[EVENT_WINDOW_VALUE] = int(request.GET[EVENT_WINDOW_VALUE])

    return HttpResponse('hello world')


def clustering(request):
    if not type(original_data_frame) is pandas.core.frame.DataFrame:
        return redirect(UPLOAD_PATH)

    if request.method == GET:
        context = file_helper.load_data(request.session['filename'], original_data_frame)
        return render(request, CLUSTERING_PAGE, context)
    if request.method == POST:
        columns = request.POST.getlist('column')
        cluster_method = request.POST[CLUSTERING_METHOD]
        number_of_clusters = int(request.POST[NUMBER_OF_CLUSTERS])

        data_frame = file_helper.remove_columns(columns, original_data_frame)
        global current_data_frame
        apply_clustering(cluster_method, number_of_clusters, original_data_frame,
                         data_frame)  # todo should pass current data frmae
        current_data_frame['clusterID'] = original_data_frame['clusterID']
        return redirect(PREPROCESSOR_PATH)


def preprocessor(request):
    if not type(original_data_frame) is pandas.core.frame.DataFrame:
        return redirect(UPLOAD_PATH)

    if request.method == 'POST':
        columns = request.POST.getlist('column')
        vistype = request.POST.get('visualization')
        global current_data_frame
        current_data_frame = file_helper.remove_columns(columns, current_data_frame)
        if vistype == 'parellel':
            return redirect(VISUALIZE_PATH)
        elif vistype == 'sunburst':
                return redirect(SUNBURST_PATH)
        return redirect(VISUALIZE_PATH)
    else:
        context = file_helper.load_data(request.session['filename'], current_data_frame)
        return render(request, PREPROCESSOR_PAGE, context)


def upload(request):
    if request.method == 'POST':
        response_data = {}
        try:
            input_file = request.FILES['fileinput']
            output = file_helper.handle_uploaded_file(input_file,0)

            if output['success']:
                global original_data_frame, current_data_frame
                original_data_frame = output['dataframe']

                original_data_frame.columns = file_helper.get_html_friendly_names(original_data_frame.columns)
                current_data_frame = original_data_frame.copy(deep=True)

                request.session['filename'] = input_file.name

                response_data['file_name'] = input_file.name
                response_data['success'] = True
            else:
                if output['error'] == 'PARSE-ERROR':
                    response_data = output
                else:
                    response_data['error'] = output['error']
                    response_data['success'] = False

        except Exception, error:
            response_data['error'] = "Error while setting up file. Please try again."
            response_data['success'] = False

        return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        return render(request, 'vivarana/upload.html', {})


def rule_gen(request):
    if request.method == 'POST':
        rule_list = rule_generator.generate(request.body, current_data_frame)
        json_response = json.dumps({'rules': rule_list})
        return HttpResponse(json_response)
    else:
        print request.GET['selected_ids']
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

    #logger.debug(request)
    return render(request, 'vivarana/sunburst.html')

def get_tree_data(request):
    json_tree = ct.build_json_hierarchy(current_data_frame.values)
    return HttpResponse(json_tree)



