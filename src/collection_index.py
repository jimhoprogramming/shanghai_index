# -*- coding: utf-8 -*-
import re
import collection_data as cd


def get_url():
    return cd.read_url_aimname(Feature_class_name = 'Index_Feature')

def get_value(url):
    return cd.get_value(url)    


def run(data = {}):
    urls = get_url()
    actual_access_urls = []
    for url in urls:
        actual_access_urls.append(url[1])
    actual_access_urls = list(set(actual_access_urls))
    rel = list(map(get_value, actual_access_urls))
    #print(rel)
    for url in urls:
        i = actual_access_urls.index(url[1])
        if url[-1] not in ['abc']:
            value = cd.clear_data(rel[i], url[-1])
        else:
            h = float(cd.clear_data(rel[i], url[-2]))
            l = float(cd.clear_data(rel[i], url[-3]))
            c = float(cd.clear_data(rel[i], url[-4]))
            value =  abs(h - l)/ c * 100
        print('{} = {}'.format(url[0],value))
        data[url[0]] = [value]
    return data
