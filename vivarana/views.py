import json
import pandas

from django.http import HttpResponse
from django.shortcuts import render, redirect

from helper import file_helper
from helper import aggregate
from rulegen import cart_based_rule_generator as rule_generator
from helper.cluster import *


original_data_frame = None
current_data_frame = None

properties_map = {}


def home(request):
    context = {}
    return render(request, 'vivarana/home.html', context)


def visualize(request):
    if not type(original_data_frame) is pandas.core.frame.DataFrame:
        return redirect(UPLOAD_PATH)

    column_types = file_helper.get_compatible_column_types(current_data_frame)
    json_output = current_data_frame.to_json(orient='records')
    return render(request, 'vivarana/visualize.html',
                  {'columns': column_types, 'result': json_output, 'frame_size': len(current_data_frame)})


def aggregator(request):
    new_data_frame = aggregate.aggregate_window(int(request.GET['aggregate_func']), properties_map['time_window_value'],
                                                properties_map['time_granularity'],
                                                request.GET['attribute_name'], original_data_frame, current_data_frame)
    json = new_data_frame.to_json(orient='records')
    return HttpResponse(json)


def set_time(request):
    properties_map['time_granularity'] = request.GET['time_granularity']
    properties_map['time_window_value'] = request.GET['time_window_val']
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
        global current_data_frame
        current_data_frame = file_helper.remove_columns(columns, current_data_frame)
        return redirect(VISUALIZE_PATH)
    else:
        context = file_helper.load_data(request.session['filename'], current_data_frame)
        return render(request, PREPROCESSOR_PAGE, context)


def upload(request):
    if request.method == 'POST':
        response_data = {}
        try:
            input_file = request.FILES['fileinput']

            output = file_helper.handle_uploaded_file(input_file)

            if output['success']:
                global original_data_frame, current_data_frame
                original_data_frame = output['dataframe']
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

        except Exception, e:
            print str(e)
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
        json_responce = "{'message' : done!}"
        return HttpResponse(json_responce)


def reset_axis(request):
    if request.method == GET:
        attribute_name = request.GET['attribute_name']
        current_data_frame[attribute_name] = original_data_frame[attribute_name]
        json = current_data_frame.to_json(orient='records')
        return HttpResponse(json)



