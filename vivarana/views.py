import json

from django.http import HttpResponse
from django.shortcuts import render, redirect
from helper import file_helper
from helper import aggregate

original_data_frame = ""
current_data_frame = ""

parameters_map = {}


def home(request):
    context = {}
    return render(request, 'vivarana/home.html', context)


def visualize(request):
    json = current_data_frame.to_json(orient='records')
    return render(request, 'vivarana/visualize.html', {'result': json, 'frame_size': len(current_data_frame)})


def paracoords(request):
    return render(request, 'vivarana/paracoords.html', {})


def get_sum(request):
    attribute_name = request.GET['attribute_name']
    new_data_frame = aggregate.sum_of_window(parameters_map['time_window_value'], parameters_map['time_granularity'],
                                             attribute_name, current_data_frame)
    json = new_data_frame.to_json(orient='records')
    return HttpResponse(json)


def set_time(request):
    parameters_map['time_granularity'] = request.GET['time_granularity']
    parameters_map['time_window_value'] = request.GET['time_window_val']
    return HttpResponse('hello world')


def preprocessor(request):
    if request.method == 'POST':
        columns = request.POST.getlist('column')
        global current_data_frame
        current_data_frame = file_helper.remove_columns(columns, original_data_frame)
        return redirect('/vivarana/visualize')
    else:
        context = file_helper.load_data(request.session['filename'], original_data_frame)
        return render(request, 'vivarana/preprocessor.html', context)


def upload(request):
    if request.method == 'POST':
        response_data = {}
        try:
            input_file = request.FILES['fileinput']

            output = file_helper.handle_uploaded_file(input_file)

            if output['success']:
                global original_data_frame, current_data_frame
                original_data_frame = output['dataframe']
                current_data_frame = original_data_frame

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




