from django.http import HttpResponseRedirect
from django.shortcuts import render, render_to_response
from .forms import UploadFileForm
import csv
import scipy as sp
import numpy as np
import pandas as pd
import json

def home(request):
    context = { }
    return render(request, 'vivarana/home.html', context)

def visualize(request):
    context = loadData(request.session['filename'],request)
    return render(request, 'vivarana/visualize.html', context)

def dvis(request):
    context = { }
    return render(request, 'vivarana/d3.html', context)

def upload(request):
    if request.method=='POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            request.session['filename'] = request.FILES['file'].name

            print request.session['filename']
            return HttpResponseRedirect('/vivarana/visualize')
    else:
        form = UploadFileForm()
    return render(request, 'vivarana/upload.html', {'form': form})

def handle_uploaded_file(fileIn):
    with open("media/"+fileIn.name, 'wb+') as destination:
        for chunk in fileIn.chunks():
            destination.write(chunk)

def loadData(fileName , request):
    print 'media/'+fileName
    count = 0

    with open('media/'+fileName,'r') as csvfile:
        dataframe = pd.read_csv(csvfile)
        cols = list(dataframe.columns)
        to_json(dataframe, 'media/data.json')
    print count

    return {"filename" : fileName, "columns": cols}

def to_json(df,filename):
    d = [
        dict([
            (colname, row[i])
            for i,colname in enumerate(df.columns)
        ])
        for row in df.values
    ]
    return json.dump(d, open(filename + '.json', 'w'))