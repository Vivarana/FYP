import os
import datetime
from sklearn.metrics import confusion_matrix

from numpy import *
from pandas.io import json
from rpy2.robjects.packages import importr
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
import rpy2.robjects as robjects
import pandas.rpy.common as com

import rule as rule_classes
import vivarana.constants as constants


debug = True

data_types = None
r_code = '''
descendants <- function(nodes, include = TRUE)
{
    n <- length(nodes)
    if (n == 1L) return(matrix(TRUE, 1L, 1L))
    ind <- 1:n
    desc <- matrix(FALSE, n, n)
    if (include) diag(desc) <- TRUE
    parents <- match((nodes %/% 2L), nodes)
    lev <- floor(log(nodes, base = 2))
    desc[1L, 2L:n] <- TRUE
    for (i in max(lev):2L) {
        desc[cbind(ind[parents[lev == i]], ind[lev == i])] <- TRUE
        parents[lev == i] <- parents[parents[lev == i]]
        lev[lev == i] <- i - 1L
    }
    desc
}

mypath <- function(tree, nodes, pretty = 0, print.it = TRUE)
{
    if (!inherits(tree, "rpart"))
        stop("Not a legitimate \\"rpart\\" object")
    splits <- labels(tree, digits=25, pretty = pretty)
    frame <- tree$frame
    n <- row.names(frame)
    node <- as.numeric(n)
    which <- descendants(node)          # ancestors are columns
    path <- list()
    if (missing(nodes)) {
        xy <- rpartco(tree)
        while(length(i <- identify(xy, n = 1L, plot = FALSE)) > 0L) {
            path[[n[i]]] <- path.i <- splits[which[, i]]
            if (print.it) {
                cat("\\n", "node number:", n[i], "\\n")
                cat(paste("  ", path.i), sep = "\\n")
            }
        }
    } else {
        if (length(nodes <- match(nodes, node)) == 0L)
            return(invisible())
        for (i in nodes) {
            path[[n[i]]] <- path.i <- splits[which[, i]]
            if (print.it) {
                cat("\\n", "node number:", n[i], "\\n")
                cat(paste("  ", path.i), sep = "\\n")
            }
        }
    }
    invisible(path)
}

rules <- function(model)
{
  if (!inherits(model, "rpart")) stop("Not a legitimate rpart tree")

  frm     <- model$frame
  names   <- row.names(frm)
  ylevels <- attr(model, "ylevels")
  ds.size <- model$frame[1,]$n

  rulelist <- character()
  coverage <- numeric()
  #yval <- character()


  for (i in 1:nrow(frm))
  {
    if (frm[i,1] == "<leaf>")
    {
      pth <- mypath(model, nodes=as.numeric(names[i]), print.it=FALSE)
      if(ylevels[frm[i,]$yval] == 1){
        rule <- unname(unlist(pth))[-1]
        rule <- paste(rule, collapse = "_AND_")
       rulelist[length(rulelist)+1] <- rule
       coverage[length(coverage)+1] <- unname(frm[i,]$n)
      }
    }
  }
  #rulelist
  data.frame(rulelist,coverage, stringsAsFactors=FALSE)
}
'''


def merge_rules(rule1, rule2):
    # Handle the merging when both operations are equal. And when one is '='
    if rule1['operation'] == '=':
        if rule2['operation'] == '=':
            return {'operation': '=', 'operand': set(rule1['operand']) & set(rule2['operand'])}
        else:
            return {'operation': '=', 'operand': rule1['operand']}
    elif rule2['operation'] == '=':
        return {'operation': '=', 'operand': rule2['operand']}
    elif rule1['operation'] == '<' and rule2['operation'] == '<':
        return {'operation': '<', 'operand': [min([num(rule1['operand']), num(rule2['operand'])])]}
    elif rule1['operation'] == '>' and rule2['operation'] == '>':
        return {'operation': '>', 'operand': [max([num(rule1['operand']), num(rule2['operand'])])]}
    elif rule1['operation'] == '<=' and rule2['operation'] == '<=':
        return {'operation': '<=', 'operand': [min([num(rule1['operand']), num(rule2['operand'])])]}
    elif rule1['operation'] == '>=' and rule2['operation'] == '>=':
        return {'operation': '>=', 'operand': [max([num(rule1['operand']), num(rule2['operand'])])]}

    operations = [rule1['operation'], rule2['operation']]
    operands = [rule1['operand'], rule2['operand']]

    if '>' in operations:
        op_index = operations.index('>')
        # > and <
        if operations[(op_index + 1) % 2] == '<':
            return {'operation': '<>', 'operand': sorted(operands)}
        # > and <=
        if operations[(op_index + 1) % 2] == '<=':
            return {'operation': '<=>', 'operand': sorted(operands)}
        # > and >=
        if operations[(op_index + 1) % 2] == '>=':
            if max(operands) == operands[op_index]:
                return {'operation': '>', 'operand': [max(operands)]}
            else:
                return {'operation': '>=', 'operand': [max(operands)]}
    elif '<' in operations:
        op_index = operations.index('<')
        # < and >=
        if operations[(op_index + 1) % 2] == '>=':
            return {'operation': '<>=', 'operand': sorted(operands)}
        # < and <=
        if operations[(op_index + 1) % 2] == '<=':
            if max(operands) == operands[op_index]:
                return {'operation': '<', 'operand': [min(operands)]}
            else:
                return {'operation': '<=', 'operand': [min(operands)]}
    elif '<=' in operations and '>=' in operations:
        return {'operation': '<=>=', 'operand': [min(operands)]}


def parse_rule(rule_list, aggregate_functions):
    rules = rule_list.split('_AND_')

    rule_dict = {}

    for rule in rules:
        if '<=' in rule:
            rule_variable, rule_parameters = rule.split('<=')
            if rule_variable in rule_dict.keys():
                rule_dict[rule_variable] = merge_rules(rule_dict[rule_variable],
                                                       num(rule_parameters.split(',')[-1], rule_variable))
            else:
                rule_dict[rule_variable] = {'operation': '<=',
                                            'operand': num(rule_parameters.split(',')[-1], rule_variable)}
        elif '>=' in rule:
            rule_variable, rule_parameters = rule.split('>=')
            if rule_variable in rule_dict.keys():
                rule_dict[rule_variable] = merge_rules(rule_dict[rule_variable],
                                                       {'operation': '>=',
                                                        'operand': num(rule_parameters.split(',')[-1], rule_variable)})
            else:
                rule_dict[rule_variable] = {'operation': '>=',
                                            'operand': num(rule_parameters.split(',')[-1], rule_variable)}
        elif '=' in rule:
            splits = rule.split('=')
            rule_variable = splits[0]
            rule_parameters = splits[1]
            if rule_variable in rule_dict.keys():
                rule_dict[rule_variable] = merge_rules(rule_dict[rule_variable],
                                                       {'operation': '=', 'operand': rule_parameters.split(',')})
            else:
                rule_dict[rule_variable] = {'operation': '=', 'operand': rule_parameters.split(',')}
        elif '<' in rule:
            rule_variable, rule_parameters = rule.split('<')
            if rule_variable in rule_dict.keys():
                rule_dict[rule_variable] = merge_rules(rule_dict[rule_variable],
                                                       {'operation': '<',
                                                        'operand': num(rule_parameters.split(',')[-1], rule_variable)})
            else:
                rule_dict[rule_variable] = {'operation': '<',
                                            'operand': num(rule_parameters.split(',')[-1], rule_variable)}
        elif '>' in rule:
            rule_variable, rule_parameters = rule.split('>')
            if rule_variable in rule_dict.keys():
                rule_dict[rule_variable] = merge_rules(rule_dict[rule_variable],
                                                       {'operation': '>',
                                                        'operand': num(rule_parameters.split(',')[-1], rule_variable)})
            else:
                rule_dict[rule_variable] = {'operation': '>',
                                            'operand': num(rule_parameters.split(',')[-1], rule_variable)}

    if debug:
        print "Rule parsed..."
        print rule_dict

    rule_set = []

    for rule_key in rule_dict:
        rule = rule_dict[rule_key]
        rule_set.append(rule_classes.rules[rule['operation']](rule_key, rule['operand'],
                                                              get_aggregate_function(aggregate_functions, rule_key)))

    return rule_classes.ConstraintSet('AND', rule_set)


def generate(selected_ids, dataframe, state):
    try:
        success = True
        rules = []
        global data_types
        data_types = dataframe.dtypes
        columns = dataframe.columns
        selected_ids = json.loads(selected_ids)

        #todo need to fin a way to remove deep copying twice
        # file_frame = dataframe.copy(deep=True)
        # file_frame[constants.RULEGEN_COLUMN_NAME] = 'NO'
        # file_frame[constants.RULEGEN_COLUMN_NAME][
        #     file_frame.index.isin(selected_ids['selected_ids'])] = 'YES'
        # if 'clusterID' in file_frame.columns:
        #     file_frame = file_frame.drop('clusterID', 1)
        # if 'Date' in file_frame.columns:
        #     file_frame = file_frame.drop('Date', 1)
        # file_path = "media" + os.path.sep + "rule.csv"
        # file_frame.to_csv(file_path, index=False)
        # del file_frame
        # pandas2ri.activate()
        # r_df = ro.r['read.csv'](file_path)
        # robjects.r('''
        #     library(rJava)
        #     library(RWeka)
        #     f<- function(df){
        #         rule_set <- JRip(SELECTED_FOR_RULEGEN ~ ., data = df)
        #         lst<-as.matrix(scan(text=.jcall(rule_set$classifier, "S", "toString") ,sep="\n", what="") )[ -c(1:2, 6), ,drop=FALSE]
        #         lst
        #     }
        #     ''')
        # r_f = robjects.r['f']
        # res = r_f(r_df)
        # # ru = com.convert_robj(res)
        # # print ru
        # print res
        # del r_df



        temporary_dataframe = dataframe.copy(deep=True)
        temporary_dataframe[constants.RULEGEN_COLUMN_NAME] = 0
        temporary_dataframe[constants.RULEGEN_COLUMN_NAME][
            temporary_dataframe.index.isin(selected_ids['selected_ids'])] = 1

        if 'clusterID' in temporary_dataframe.columns:
            temporary_dataframe = temporary_dataframe.drop('clusterID', 1)

        selected_columns = ' + '.join(selected_ids['checked_columns'])

        r_dataframe = com.convert_to_r_dataframe(temporary_dataframe)
        ro.r(r_code)
        rpart = importr('rpart')

        temp = rpart.rpart(constants.RULEGEN_COLUMN_NAME + ' ~ ' + selected_columns, method="class", data=r_dataframe)


        ro.r.assign('temp', temp)
        r_get_rules_function = ro.globalenv['rules']

        rule_set = com.convert_robj(r_get_rules_function(temp))

        temp_rule_set = []

        if debug:
            print temp

        for index, row in rule_set.iterrows():
            temp_rule = parse_rule(row['rulelist'], state[constants.AGGREGATE_FUNCTION_ON_ATTR])
            temp_rule_set.append(temp_rule)
            rules.append({'rule': temp_rule.to_string(), 'coverage': row['coverage']})

        constraint_set = rule_classes.ConstraintSet('OR', temp_rule_set)
        rule_applied_index = constraint_set.apply_constraint(temporary_dataframe).index

        temporary_dataframe['FILTERED_BY_RULE'] = 0
        temporary_dataframe['FILTERED_BY_RULE'][
            temporary_dataframe.index.isin(rule_applied_index)] = 1

        confusion_mat = confusion_matrix(temporary_dataframe['FILTERED_BY_RULE'], temporary_dataframe[constants.RULEGEN_COLUMN_NAME])
        precision = get_precision(confusion_mat)
        recall = get_recall(confusion_mat)

        select_string = get_aggregate_string(state[constants.AGGREGATE_FUNCTION_ON_ATTR], columns)
        window_string = get_window_string(state)

        if debug:
            print constraint_set.to_string()
            print len(dataframe), len(temporary_dataframe), len(constraint_set.apply_constraint(temporary_dataframe).index)
            print precision, recall
            print confusion_mat

        return success, rules, len(selected_ids['selected_ids']), len(rule_applied_index), precision, recall, select_string, window_string

    except Exception, e:
        print e
        return False, None, None, None, None, None, None


def get_precision(conf_matrix):
    return (conf_matrix[1][1])/float(conf_matrix[0][1] + conf_matrix[1][1])


def get_recall(conf_matrix):
    return (conf_matrix[1][1])/float(conf_matrix[1][1]+conf_matrix[1][0])


def num(s, column):
    try:
        if data_types[column] == 'datetime64[ns]':
            print float(s)
            return datetime.datetime.fromtimestamp(float(s))
        return int(s)
    except ValueError:
        return float(s)


def get_aggregate_function(state, column):
    try:
        return state[column][0]
    except Exception, e:
        return ''


def get_aggregate_string(state, columns):
    temp_col = []
    for i in xrange(len(columns)):
        aggregate = get_aggregate_function(state, columns[i])
        if aggregate != '':
            temp_col.append(aggregate + '(' + columns[i] + ') AS ' + aggregate + '_' + columns[i])
        else:
            temp_col.append(columns[i])

    return ', '.join(temp_col)


def get_window_string(state_map):
    if not (state_map[constants.WINDOW_TYPE] is None):
        window_string = '#window.' + state_map[constants.WINDOW_TYPE]
        if state_map[constants.WINDOW_TYPE] == constants.TIME_WINDOW:
            window_string = window_string + '(' + str(state_map[constants.TIME_WINDOW_VALUE]) + ' ' + str(
                state_map[constants.TIME_GRANULARITY]) + ')'
        else:
            window_string = window_string + '(' + str(state_map[constants.EVENT_WINDOW_VALUE]) + ')'

        return window_string
    else:
        return ''