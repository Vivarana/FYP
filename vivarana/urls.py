from django.conf.urls import patterns, url

from vivarana import views

urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
    url(r'^upload/$', views.upload , name='upload'),
    url(r'^preprocessor/$', views.preprocessor, name='preprocessor'),
    url(r'^visualize/$', views.visualize , name='visualize'),
    url(r'^paracoords/$', views.paracoords , name='paracoords'),
    # url(r'^d3/$',views.dvis , name='d3'),
    # # ex: /polls/5/
    # url(r'^(?P<question_id>\d+)/$', views.detail, name='detail'),
    # # ex: /polls/5/results/
    # url(r'^(?P<question_id>\d+)/results/$', views.results, name='results'),
    # # ex: /polls/5/vote/
    # url(r'^(?P<question_id>\d+)/vote/$', views.vote, name='vote'),
)