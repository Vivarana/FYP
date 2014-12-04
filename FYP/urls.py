from django.conf.urls import patterns, include, url
from django.conf import settings

# from django.contrib import admin

urlpatterns = patterns('',

    url(r'^', include('vivarana.urls', namespace='vivarana')),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT})

)
