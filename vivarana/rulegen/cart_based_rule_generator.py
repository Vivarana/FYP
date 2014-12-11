from numpy import *
from pandas.io import json
import rpy2.robjects as ro
import pandas.rpy.common as com
from rpy2.robjects.packages import importr

import vivarana.constants as constants

r_code = '''rules <- function(model)
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
      pth <- path.rpart(model, nodes=as.numeric(names[i]), print.it=FALSE)
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
        return {'operation': '<', 'operand': [min([float(rule1['operand'][0]), float(rule2['operand'][0])])]}
    elif rule1['operation'] == '>' and rule2['operation'] == '>':
        return {'operation': '>', 'operand': [max([float(rule1['operand'][0]), float(rule2['operand'][0])])]}
    elif rule1['operation'] == '<=' and rule2['operation'] == '<=':
        return {'operation': '<=', 'operand': [min([float(rule1['operand'][0]), float(rule2['operand'][0])])]}
    elif rule1['operation'] == '>=' and rule2['operation'] == '>=':
        return {'operation': '>=', 'operand': [max([float(rule1['operand'][0]), float(rule2['operand'][0])])]}

    operations = [rule1['operation'], rule2['operation']]
    operands = [float(rule1['operand'][0]), float(rule2['operand'][0])]

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


def parse_rule(rule_list):
    rules = rule_list.split('_AND_')

    rule_dict = {}
    rule_strings = []
    for rule in rules:
        print rule
        if '<=' in rule:
            rule_variable, rule_parameters = rule.split('<=')
            if rule_variable in rule_dict.keys():
                rule_dict[rule_variable] = merge_rules(rule_dict[rule_variable], rule_parameters.split(','))
            else:
                rule_dict[rule_variable] = {'operation': '<=',
                                            'operand': {'operation': '<=', 'operand': rule_parameters.split(',')}}
        elif '>=' in rule:
            rule_variable, rule_parameters = rule.split('>=')
            if rule_variable in rule_dict.keys():
                rule_dict[rule_variable] = merge_rules(rule_dict[rule_variable],
                                                       {'operation': '>=', 'operand': rule_parameters.split(',')})
            else:
                rule_dict[rule_variable] = {'operation': '>=', 'operand': rule_parameters.split(',')}
        elif '=' in rule:
            splits = rule.split('=')
            rule_variable = splits[0]
            rule_parameters = ''.join(splits[1:])
            if rule_variable in rule_dict.keys():
                rule_dict[rule_variable] = merge_rules(rule_dict[rule_variable],
                                                       {'operation': '=', 'operand': rule_parameters.split(',')})
            else:
                rule_dict[rule_variable] = {'operation': '=', 'operand': rule_parameters.split(',')}
        elif '<' in rule:
            rule_variable, rule_parameters = rule.split('<')
            if rule_variable in rule_dict.keys():
                rule_dict[rule_variable] = merge_rules(rule_dict[rule_variable],
                                                       {'operation': '<', 'operand': rule_parameters.split(',')})
            else:
                rule_dict[rule_variable] = {'operation': '<', 'operand': rule_parameters.split(',')}
        elif '>' in rule:
            rule_variable, rule_parameters = rule.split('>')
            if rule_variable in rule_dict.keys():
                rule_dict[rule_variable] = merge_rules(rule_dict[rule_variable],
                                                       {'operation': '>', 'operand': rule_parameters.split(',')})
            else:
                rule_dict[rule_variable] = {'operation': '>', 'operand': rule_parameters.split(',')}

    print "Rules processed. Now merging them together and parsing as CEP rule.."
    print rule_dict

    for rule_key in rule_dict:
        rule = rule_dict[rule_key]
        if rule['operation'] == '=':
            rule_strings.append(rule_key + rule['operation'] + ' OR '.join(rule['operand']))
        elif rule['operation'] == '<=>':
            rule_strings.append(str(int(rule['operand'][0])) + ' <= ' + rule_key + ' < ' + str(int(rule['operand'][1])))
        elif rule['operation'] == '<>=':
            rule_strings.append(str(int(rule['operand'][0])) + ' < ' + rule_key + ' <= ' + str(int(rule['operand'][1])))
        elif rule['operation'] == '<=>=':
            rule_strings.append(
                str(int(rule['operand'][0])) + ' <= ' + rule_key + ' <= ' + str(int(rule['operand'][1])))
        else:
            rule_strings.append(rule_key + rule['operation'] + str(int(float(rule['operand'][0]))))

    rule_strings.sort(key=len)
    print "Combining all the rules together."
    print rule_strings
    final_rule = ' AND </br>'.join(rule_strings)
    return final_rule


# def remove_unique_columns(temporary_dataframe):
# row_count = len(temporary_dataframe.index)
# for column in temporary_dataframe.columns:
# print column, len(pd.unique(temporary_dataframe[column])), row_count*0.25  # todo: fix the ratio
# if len(pd.unique(temporary_dataframe[column])) > row_count*0.8:
# temporary_dataframe = temporary_dataframe.drop(column, 1)
#     return temporary_dataframe


def generate(selected_ids, dataframe):
    try:
        rules = []
        selected_ids = json.loads(selected_ids)

        temporary_dataframe = dataframe.copy(deep=True)
        temporary_dataframe[constants.RULEGEN_COLUMN_NAME] = 0
        temporary_dataframe[constants.RULEGEN_COLUMN_NAME][
            temporary_dataframe.index.isin(selected_ids['selected_ids'])] = 1

        if 'clusterID' in temporary_dataframe.columns:
            temporary_dataframe = temporary_dataframe.drop('clusterID', 1)

        selected_columns = ' + '.join(selected_ids['checked_columns'])
        print selected_columns

        r_dataframe = com.convert_to_r_dataframe(temporary_dataframe)
        ro.r(r_code)
        rpart = importr('rpart')
        temp = rpart.rpart(constants.RULEGEN_COLUMN_NAME + ' ~ ' + selected_columns, method="class", data=r_dataframe)

        ro.r.assign('temp', temp)
        r_get_rules_function = ro.globalenv['rules']

        rule_set = com.convert_robj(r_get_rules_function(temp))
        print temp
        for index, row in rule_set.iterrows():
            rules.append({'rule': parse_rule(row['rulelist']), 'coverage': row['coverage']})

        print rules
        return rules

    except Exception, e:
        print e
        return "error!"


