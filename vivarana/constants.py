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

# error
ERROR_100 = 'error-100'  # aggregate error where aggregation is performed without setting window value

#file upload constant
FILE_INPUT = 'fileinput'  # fileinput of the form

#supported file extensions
EXT_CSV = 'csv'
EXT_LOG = 'log'

#temp file
TEMP_FILE_PATH = 'media' + os.path.sep + 'temp'

# state map properties
DATA_LST = "data_lst"
CURRENT_ROW_IDS_LST = 'current_row_ids_lst'
CLUSTER_IDS_DICT = 'cluster_ids_dict'
CURRENT_PAGE_NUMBER = 'current_page_number'

ACTIVE_PAGE_NUMBER = 'active_page_number'

PAGINATION_METHOD = 'pagination_method'
PAGE_SIZE = 'page_size'
NUMBER_PAGES = 'number_pages'

CLUSTER_COLUMNS_LST = 'cluster_columns_lst'

ANOMALY_DETECT_COLUMN = 'anomaly_detect_column'
ANOMALY_DICT = 'anomaly_dict'

AGGREGATE_FUNCTION_ON_ATTR = 'aggregate_function_on_attribute'
ALL_ATTRIBUTE_LST = 'all_attribute_lst'
REMOVED_ATTRIBUTE_LST = 'removed_attribute_lst'
AGGREGATE_GROUP_BY_ATTR = 'aggregate_group_by_attr'

BRUSH_MODE = 'brush_mode'
ONE_BRUSH = '1D-axes'
TWO_BRUSH = '2D-strums'

BUNDLING_ENABLED = 'bundling_enabled'
CLUSTER_COLORING_ENABLED = 'cluster_coloring_enabled'
ZSCORE_COLORING_ENABLED = 'zscore_coloring_enabled'
ALPHA_BLENDING_ENABLED = 'alpha_blending_enabled'

BUNDLING_STRENGTH = 'bundling_strength'
CURVE_SMOOTHNESS = 'curve_smoothness'
ALPHA_OPACITY = 'alpha_opacity'

TIME_WINDOW_ENABLED = 'time_window_enabled'

PROPERTY_NAME = 'property_name'
PROPERTY_VALUE = 'property_value'


#aggregate functions

SUM = 'sum'
AVG = 'average'
MIN = 'min'
MAX = 'max'
COUNT = 'count'

# preprocesser page
PARACOORDS_VIS_TYPE = 'Parallel Coordinates'
SUNBURST_VIS_TYPE = 'Sunburst'
GROUPING_COL_NAME = 'grouping_col_name'
GROUPED_COL_NAME = 'grouped_col_name'

