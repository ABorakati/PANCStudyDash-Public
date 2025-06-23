# -*- coding: utf-8 -*-
"""
Created on Sat Mar 13 14:04:26 2021
@author: abora
"""
import requests
from bokeh.embed import file_html
from bokeh.resources import CDN
from bokeh.io import reset_output, save, curdoc
from bokeh.layouts import row, column, widgetbox
from bokeh.client import push_session

import numpy as np

import pandas as pd

from bokeh.plotting import figure, output_file, show, curdoc
from bokeh.models import (
    Band,
    ColumnDataSource,
    HoverTool,
    Slider,
    Range1d,
    DataTable,
    TableColumn,
    Toggle,
    Column,
    Label,
)
from bokeh.models.widgets import Slider, TextInput
from datetime import datetime


logs = pd.read_csv("log.csv")
logs = logs.sort_values(["Time / Date", "Username", "Action"])
logs["Time / Date"] = pd.to_datetime(logs["Time / Date"])
logs.Action = logs.Action.str.replace("\d+", "")
logs["timediff"] = abs(
    logs["Time / Date"] - pd.to_datetime("2021-02-28 00:00:00")
).dt.total_seconds() / (24 * 60 * 60)
logs["recordcount"] = (logs["Action"] == "Created Record -").cumsum()


# Bokeh Datatable

data = {
    "token": NaN,
    "content": "report",
    "format": "json",
    "report_id": "3171",
    "csvDelimiter": "",
    "rawOrLabel": "label",
    "rawOrLabelHeaders": "label",
    "exportCheckboxLabel": "false",
    "returnFormat": "json",
}
r = requests.post("https://redcap.slms.ucl.ac.uk/api/", data=data)

count = pd.DataFrame.from_dict(r.json())
count = count.groupby("redcap_data_access_group")[
    "record_id"].nunique().reset_index()

total = count["record_id"].sum()
total = str(total) + " Patients Recruited"

count = count.sort_values(by="record_id", ascending=False)
count = count.head(20).reset_index(drop=True)
count.index = count.index + 1
count = count.reset_index()
count = count.rename(
    columns={
        "index": "#",
        "redcap_data_access_group": "Hospital",
        "record_id": "Number of Patients",
    }
)


source2 = ColumnDataSource(count)
data_table = DataTable(
    columns=[TableColumn(field=Ci, title=Ci) for Ci in count.columns],
    source=source2,
    height=600,
    index_position=None,
    autosize_mode="fit_viewport"
)
data_table.sizing_mode = "stretch_both"

# Bokeh
x = logs["timediff"]
y = logs["recordcount"]
source1 = ColumnDataSource(data=dict(x=x, y=y))
p = figure(
    title="PANC Study Recruitment",
    x_axis_label="Days",
    y_axis_label="Number of Patients",
    toolbar_location=None,
)
p.line(x="x", y="y", legend_label="Number of Patients",
       source=source1, line_width=5)
p.xaxis.axis_label = "Day"
p.yaxis.axis_label = "Number of Patients"
p.legend.location = "top_left"
p.title.align = "center"
p.x_range = Range1d(x.min(), x.max())
p.y_range = Range1d(y.min(), (y.max() + 50))
p.axis.minor_tick_line_color = None
p.xgrid.visible = False
p.ygrid.visible = False
p.varea(x=x, y1=0, y2=y, alpha=0.6)
hover = HoverTool()
hover.tooltips = [
    ("Day", "@x"),
    ("Number of Patients", "@y"),
]
N = 1

totallabel = Label(
    x=25,
    y=100,
    x_units="data",
    y_units="data",
    text=total,
    render_mode="css",
    border_line_color="black",
    border_line_alpha=0,
    background_fill_color="white",
    background_fill_alpha=0,
    text_color="#ffffff",
    text_font_style="bold",
)
p.add_tools(HoverTool(tooltips=hover.tooltips, mode="vline"))
p.add_layout(totallabel)


p.sizing_mode = "stretch_both"


curdoc().title = "PANC Study Dashboard"
curdoc().add_root(row(p, data_table))
