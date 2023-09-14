import logging
from functools import reduce
from itertools import groupby
from types import NoneType
from typing import List, Dict, Union


def list_dict_group(data: List[Dict], key):
    new_data = {"list_data": list(), "dict_data": dict()}
    data.sort(key=lambda x: x.get(key, ""))
    group_data = groupby(data, key=lambda x: x.get(key, ""))
    for data_key, values in group_data:
        _values = list(values)
        new_data["list_data"].append({"key": data_key, "values": _values})
        new_data["dict_data"].update({data_key: _values})

    return new_data


def remove_list_dict_duplicate(list_dict_data):
    """
    去除列表字典里的重复数据
    :param list_dict_data: 列表字典
    :return:
    """
    return reduce(lambda x, y: x if y in x else x + [y], [[], ] + list_dict_data)


def retry(func, params: Union[dict, list, tuple, NoneType], check_func, num=1):
    """
    执行失败重试
    :param func: 要执行的函数
    :param params: 要执行的函数的参数值
    :param check_func: 校验函数
    :param num: 重试次数
    :return:
    """
    result = None
    for i in range(num):
        try:
            if params:
                if isinstance(params, dict):
                    result = func(**params)
                elif isinstance(params, list) or isinstance(params, tuple):
                    result = func(*params)
                else:
                    break
            else:
                result = func()
            flag = check_func(result)
            if flag:
                break
        except Exception as e:
            logging.error(f"error={e}")
    return result
