import simplejson
from django.core import serializers
from django.http import HttpResponseRedirect

from django.shortcuts import render, render_to_response
from .forms import UploadFileForm
import csv
import scipy as sp
import numpy as np
import pandas as pd
import json

original_data_frame = ""


def home(request):
    context = {}
    return render(request, 'vivarana/home.html', context)


def visualize(request):
    json = original_data_frame.to_json(orient='records')
    return render(request, 'vivarana/visualize.html', {'result': json, 'frame_size': len(original_data_frame)})


def preprocessor(request):
    context = loadData(request.session['filename'])
    return render(request, 'vivarana/preprocessor.html', context)


def upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            request.session['filename'] = request.FILES['file'].name

            return HttpResponseRedirect('/vivarana/preprocessor')
    else:
        form = UploadFileForm()
    return render(request, 'vivarana/upload.html', {'form': form})


def handle_uploaded_file(fileIn):
    with open("media/" + fileIn.name, 'wb+') as destination:
        for chunk in fileIn.chunks():
            destination.write(chunk)


def loadData(fileName):
    with open('media/' + fileName, 'r') as csv_file:
        global original_data_frame
        original_data_frame = pd.read_csv(csv_file)
        cols = list(original_data_frame.columns)
    return {"filename": fileName, "columns": cols}

