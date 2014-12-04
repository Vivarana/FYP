from django.conf.urls import patterns, url

from vivarana import views

urlpatterns = patterns('',

    url(r'^$', views.home, name='home'),
    url(r'^upload/$', views.upload , name='upload'),
    url(r'^preprocessor/$', views.preprocessor, name='preprocessor'),
    url(r'^clustering/$', views.clustering, name='clustering'),
    url(r'^visualize/$', views.visualize , name='visualize'),
    url(r'^sunburst/$', views.sunburst, name='sunburst'),
    url(r'^set_time_window/$', views.set_time, name='set_time'),
    url(r'^aggregator/$', views.aggregator, name='aggregator'),
    url(r'^rule_gen/$', views.rule_gen, name='rule_gen'),
)