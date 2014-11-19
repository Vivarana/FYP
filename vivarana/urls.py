from django.conf.urls import patterns, url

from vivarana import views

urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
    url(r'^upload/$', views.upload , name='upload'),
    url(r'^preprocessor/$', views.preprocessor, name='preprocessor'),
    url(r'^visualize/$', views.visualize , name='visualize'),
    url(r'^paracoords/$', views.paracoords , name='paracoords'),
)