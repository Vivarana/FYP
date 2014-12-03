from numpy import *
from pandas.io import json
import scipy as sp
from pandas import *
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri
import rpy2.robjects as ro
import pandas.rpy.common as com
from pandas import DataFrame


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


def merge_rules_categorical_and(rule1, rule2):
    return set(rule1) & set(rule2)


def parse_rule(rule_list):
    rules = rule_list.split('_AND_')
    rule_dict = {}
    ruleStrings = []
    for rule in rules:
        if '=' in rule:
            rule_variable, rule_parameters = rule.split('=')
            if rule_variable in rule_dict.keys():
                rule_dict[rule_variable] = merge_rules_categorical_and(rule_dict[rule_variable] , rule_parameters.split(','))
            else:
                rule_dict[rule_variable] = rule_parameters.split(',')

    for key in rule_dict:
        rule = rule_dict[key]
        ruleStrings.append(key + " = " + ' OR '.join(rule))

    final_rule = ' AND '.join(ruleStrings)
    print final_rule
    return final_rule


def generate(selected_ids, dataframe):
    try:
        rules = []
        selected_ids = json.loads(selected_ids)
        temporary_dataframe = dataframe.copy(deep=True)
        temporary_dataframe["SELECTED_FOR_RULEGEN"] = 0
        temporary_dataframe["SELECTED_FOR_RULEGEN"][temporary_dataframe.index.isin(selected_ids)] = 1

        r_dataframe = com.convert_to_r_dataframe(temporary_dataframe)
        ro.r(r_code)
        rpart = importr('rpart')
        temp = rpart.rpart('SELECTED_FOR_RULEGEN ~ .', method="class", data=r_dataframe)

        ro.r.assign('temp', temp)
        r_get_rules_function = ro.globalenv['rules']

        rule_set = com.convert_robj(r_get_rules_function(temp))
        for index, row in rule_set.iterrows():
            rules.append({'rule': parse_rule(row['rulelist']), 'coverage': row['coverage']})

        print rules
        return rules

    except Exception, e:
        print e
        return "error!"


