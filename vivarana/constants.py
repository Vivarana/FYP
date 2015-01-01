import os

# HTTP methods
POST = 'POST'
GET = 'GET'

# Clustering page constants
CLUSTERING_METHOD = 'clustering-algo-radios'
NUMBER_OF_CLUSTERS = 'number-of-clusters'

K_MEANS_CLUSTERING = 'kmeans-cluster'
HIERARCHICAL_CLUSTERING = 'hierarchical-cluster'
FUZZY_CLUSTERING = 'fuzzy-cluster'

# HTML template paths
CLUSTERING_PAGE = 'vivarana/clustering.html'
PREPROCESSOR_PAGE = 'vivarana/preprocessor.html'
SUNBURST_PAGE = 'vivarana/sunburst.html'
HOME_PAGE = 'vivarana/home.html'

# URL paths
HOME_PATH = '/'
UPLOAD_PATH = '/upload/'
VISUALIZE_PATH = '/visualize'
PREPROCESSOR_PATH = '/preprocessor/'
SUNBURST_PATH = "/sunburst/"

# Rule generation associated constants
RULEGEN_COLUMN_NAME = "SELECTED_FOR_RULEGEN"

# time/event window constants
ATTRIBUTE_NAME = 'attribute_name'
TIME_WINDOW = 'time'
EVENT_WINDOW = 'event'
WINDOW_TYPE = 'window_type'
TIME_GRANULARITY = 'time_granularity'
TIME_WINDOW_VALUE = 'time_window_value'
EVENT_WINDOW_VALUE = 'event_window_value'

#error
ERROR_100 = 'error-100'  # aggregate error where aggregation is performed without setting window value

#file upload constant
FILE_INPUT = 'fileinput'  # fileinput of the form

#supported file extensions
EXT_CSV = 'csv'
EXT_LOG = 'log'

#temp file
TEMP_FILE_PATH = 'media' + os.path.sep + 'temp'

# preprocesser page

PARACOORDS_VIS_TYPE = 'parellel'
SUNBURST_VIS_TYPE = 'sunburst'
GROUPING_COL_NAME = 'groupby'
GROUPED_COL_NAME = 'grouped_column'