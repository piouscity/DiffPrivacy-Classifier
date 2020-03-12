import math


def entropy(value):
    result = 0
    for cls in value.count:
        prop = value.count[cls] / value.count_all
        result -= prop*math.log2(prop)
    return result


def information_gain(value, childs):
    result = entropy(value)
    for c_val in childs:
        result -= child[c_val].count_all / value.count_all \
            * entropy(child[c_val])
    return result


def exp_mechanism(edp, sensi, score):
    return math.exp(edp/(2*sensi)*score)
