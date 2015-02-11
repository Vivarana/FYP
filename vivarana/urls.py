from django.conf.urls import patterns, url

from vivarana import views

urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
    url(r'^preprocessor/$', views.preprocessor, name='preprocessor'),
    url(r'^clustering/$', views.clustering, name='clustering'),
    url(r'^visualize/$', views.visualize , name='visualize'),
    url(r'^visualize_next/$', views.visualize_next, name='visualize_next'),
    url(r'^set_window/$', views.set_window, name='set_window'),
    url(r'^change_state/$', views.change_state, name='change_state'),
    url(r'^aggregator/$', views.aggregator, name='aggregator'),
    url(r'^anomaly/$', views.anomaly, name='anomaly'),
    url(r'^rule_gen/$', views.rule_gen, name='rule_gen'),
    url(r'^reset_axis/$', views.reset_axis, name='reset_axis'),
    url(r'^remove_axis/$', views.remove_axis, name='remove_axis'),
    url(r'^current_column_lst/$', views.current_column_lst, name='current_column_lst'),
    url(r'^sunburst/$', views.sunburst, name='sunburst'),
    url(r'^tree_data/$', views.get_tree_data, name='tree_data'),
    url(r'^unique_strings/$', views.get_unique_strings, name='unique_strings'),
    url(r'^max_width/$', views.get_max_seq_width, name='max_width'),
    url(r'^apache_log_format/$', views.apache_log_format, name='apache_log_format'),
)