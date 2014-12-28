from django.conf.urls import patterns, url

from vivarana import views

urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
    url(r'^preprocessor/$', views.preprocessor, name='preprocessor'),
    url(r'^clustering/$', views.clustering, name='clustering'),
    url(r'^visualize/$', views.visualize , name='visualize'),
    url(r'^set_window/$', views.set_window, name='set_window'),
    url(r'^aggregator/$', views.aggregator, name='aggregator'),
    url(r'^rule_gen/$', views.rule_gen, name='rule_gen'),
    url(r'^reset_axis/$', views.reset_axis, name='reset_axis'),
    url(r'^sunburst/$', views.sunburst, name='sunburst'),
    url(r'^treedata/$', views.get_tree_data, name='tree_data'),
    url(r'^sessiondata$', views.get_session_sequence, name='sequences'),
    url(r'^uniqueurls/$', views.get_unique_urls, name='uniqueurls'),
)