import math


def entropy(value):
    result = 0
    for cls in value.count:
        prop = value.count[cls] / value.count_all
        result -= prop*math.log2(prop)
    return result


def information_gain(value, childs):
    result = entropy(value)
    for child in childs:
        result -= child.count_all / value.count_all * entropy(child)
    return result
