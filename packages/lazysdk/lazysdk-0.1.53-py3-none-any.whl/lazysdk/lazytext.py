#!/usr/bin/env python3
# coding = utf8
"""
@ Author : ZeroSeeker
@ e-mail : zeroseeker@foxmail.com
@ GitHub : https://github.com/ZeroSeeker
@ Gitee : https://gitee.com/ZeroSeeker
"""
import showlog
import copy
import re


def get_split(
        content: str,
        split_mark: list
):
    """
    将字符串按照指定的字符分割，返回一个list结果
    """
    split_res = list()
    for each_mark in split_mark:
        if len(split_res) == 0:
            split_res = content.split(each_mark)
        else:
            temp_split_res = list()
            for each_split_res in split_res:
                temp_split_res.extend(each_split_res.split(each_mark))
            split_res = copy.deepcopy(temp_split_res)
    return split_res


def get_url(
        content
):
    """
    从文本中获取url
    """
    content_split = get_split(content=content, split_mark=[' ', '\n'])
    url_list = list()
    for each_split in content_split:
        if 'http' in each_split and '//' in each_split:
            # 这是一个链接
            input_text_find = re.findall('http(.*?)$', each_split, re.S)
            if len(input_text_find) > 0:
                input_url = 'http%s' % input_text_find[0]
                url_list.append(input_url)
            else:
                showlog.warning('解析链接失败')
                continue
        else:
            # 这不是一个链接
            continue
    return url_list


def path_clean(content):
    """
    清除路径前后可能出现的引号
    """
    if content[0] == '"' and content[-1] == '"':
        content = content[1:-1]
    elif content[0] == '“' and content[-1] == '”':
        content = content[1:-1]
    elif content[0] == "'" and content[-1] == "'":
        content = content[1:-1]
    else:
        pass
    return content
