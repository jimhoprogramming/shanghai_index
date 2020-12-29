# -*- coding:utf-8 -*-
from pyecharts.charts import Map, Geo
from pyecharts.options import *


value = [95.1, 23.2, 43.3, 66.4, 88.5]
attr= ["China", "Canada", "Brazil", "Russia", "United States"]
data = [list(z) for z in zip(attr, value)]

init_opts = InitOpts(width = '1024px', height = '600px', theme="世界地图示例")

map0 = Map(init_opts)
map0.add(series_name = "世界地图", data_pair = data, maptype = "world", label_opts = LabelOpts(is_show=False))
map0.render(path="../data/test_world.html")
