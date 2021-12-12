import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams["font.sans-serif"] = [u"SimHei"]
mpl.rcParams["axes.unicode_minus"] = False
import pymysql
import argparse, os, sys, json
from sqlalchemy import create_engine
import tkinter as tk
from pyecharts.charts import Map
from matplotlib.pyplot import MultipleLocator
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pyecharts import options as opts

#创建写入sql的engine
parser = argparse.ArgumentParser()
parser.add_argument('-user', help="mysql database user", type=str, required=False, default='root')
parser.add_argument('-pw', help="password", type=str, required=False, default='aa88606256,,')
parser.add_argument('-host', help="ip address", type=str, required=False, default='localhost')
parser.add_argument('-db', help="database name", type=str, required=False, default='zhongjingwang')
parser.add_argument('-charset', help="character set to use", type=str, required=False, default='utf8')
sys.argv = ['-f']
args = parser.parse_args()
# helper functions
sql = lambda command: pd.read_sql(command, con)
def fetch(command):
    cursor.execute(command)
    return cursor.fetchall()
con = pymysql.connect(host=args.host, user=args.user, password=args.pw, use_unicode=True, charset=args.charset)
cursor = con.cursor()
""" insert dataset to database """
# db_data = 'mysql+pymysql://' + '<USER-NAME>' + ':' + '<PASSWORD>' + '@' + '***.***.***.***' + ':3306/' + '<DB-NAME>' + '?charset=utf8mb4'
db_data = "mysql+pymysql://{}:{}@{}:3306/{}?charset={}".format(args.user, args.pw, args.host, args.db, args.charset)
engine = create_engine(db_data).connect()
sql('use zhongjingwang')

#创建页面
window = tk.Tk()
window.title('my window')
window.geometry('800x800')

#最顶层
tk.Label(window, text='宏观经济变量分析工具 v1.0\n制作者：柯金宏\n学号：21213131').pack()

#用于选变量
frm = tk.Frame(window)
frm.pack()
frm_l = tk.Frame(frm, )
frm_m = tk.Frame(frm, )
frm_r = tk.Frame(frm)
frm_l.pack(side='left')
frm_r.pack(side='right')
frm_m.pack()

tk.Label(frm_l, text='表格').pack()

global table_var,vari_var, region_var, time1, month_var
time1 = tk.StringVar()
table_var = tk.StringVar()
vari_var = tk.StringVar()
region_var = tk.StringVar()
month_var = tk.StringVar()

def get_table():
    #选择特定表格，则更新变量信息和日期信息
    table_var.set(lb.get(lb.curselection()))#列表名
    print(table_var.get())
    get_col_sql = 'SELECT * FROM '+ table_var.get()
    col_list = [i for i in sql(get_col_sql).keys()[3:]]
    vari_list.delete(0, 'end')
    for item in col_list:
        vari_list.insert(0, item)
    # 获得当前变量的时间
    months = [i[0] for i in sql('SELECT DISTINCT 月份 FROM '+ table_var.get()).values]
    months.reverse()
    month_list.delete(0, 'end')
    for month in months:
        month_list.insert(0, month)

def get_vari():
    vari_var.set(vari_list.get(vari_list.curselection()))
    print(vari_var.get())


def get_region():
    region_var.set(region_list.get(region_list.curselection()))
    print(region_var.get())

var2 = tk.StringVar()
var2.set([i[0] for i in sql("show tables in zhongjingwang").values])
lb = tk.Listbox(frm_l, listvariable=var2)
lb.pack()
b1 = tk.Button(frm_l, text='查看表格内变量', width=15,
              height=2, command=get_table)
b1.pack()

#中间，展示对应列表的变量
tk.Label(frm_m, text='变量').pack()
vari_list = tk.Listbox(frm_m,width=40)
vari_list.pack(side='top')
b2 = tk.Button(frm_m, text='分析变量', width=15,
              height=2, command=get_vari)
b2.pack()

#右边，选择地区

tk.Label(frm_r, text='地区').pack()
var3 = tk.StringVar()
var3.set(['全国'] + [i[0] for i in sql('SELECT DISTINCT 地区 FROM 保险').values])
region_list = tk.Listbox(frm_r, listvariable=var3,width=10)
region_list.pack()
tk.Button(frm_r, text='选择地区', width=10,
              height=2, command=get_region).pack()

#选择时间
frm_time = tk.Frame(window)
frm_time.pack()

tk.Label(frm_time,text='请选择时间单位,绘制折线图：').pack()

tk.Radiobutton(frm_time, text='年',
                    variable=time1, value='SUBSTR(月份,1,4) AS 年份').pack()
tk.Radiobutton(frm_time, text='月',
                    variable=time1, value='月份').pack()

def plot_result():
    query_content = 'SELECT ' + time1.get() + ', SUM(' + vari_var.get() + ') AS ' +  vari_var.get()
    query_content += '\nFROM ' + table_var.get()
    if time1.get() == '月份':
        if region_var.get() != '全国':
            query_content += "\nWHERE 地区 = '" + region_var.get() + "'"
        query_content += '\nGROUP BY 月份'
    else:
        query_content += "\nWHERE 月份 LIKE '%12'"
        if region_var.get() != '全国':
            query_content += " AND 地区 = '" + region_var.get() + "'"
        query_content += '\nGROUP BY 年份'
    df = sql(query_content)
    print('get_df')
    f = plt.figure(figsize=(12, 8))
    f.clear()
    fig1 = plt.subplot(1, 1, 1)
    plt.plot(df.iloc[:, 0], df.iloc[:, 1], "o-")
    fig1.set_xlabel(df.keys()[0])
    fig1.set_ylabel(df.keys()[1])
    title = region_var.get() + ' ' + df.keys()[1]
    fig1.set_title(title, loc='center', pad=20, fontsize='xx-large', color='black')
    if time1.get() == '月份':
        x_major_locator = MultipleLocator(2)
        ax = plt.gca()
        ax.xaxis.set_major_locator(x_major_locator)
    print('get_plot')
    f.show()


tk.Button(frm_time, text='绘制折线图', width=10,
              height=2, command=plot_result).pack()

#生成热力图
frm_month = tk.Frame(window)
frm_month.pack()
tk.Label(frm_month, text='请选择时间段,生成全国热力图：').pack()

month_list = tk.Listbox(frm_month,width=25)
month_list.pack()
def get_month():
    month_var.set(month_list.get(month_list.curselection()))
    print(month_var.get())
    query_content = 'SELECT 地区, ' + vari_var.get() + ' FROM ' + table_var.get() + ' \nWHERE 月份 = "'+month_var.get()+'"'
    print(query_content)
    data = sql(query_content)
    max,min=data[vari_var.get()].max(),data[vari_var.get()].min()
    data = [[data['地区'][i],data[vari_var.get()][i]] for i in range(len(data['地区']))]
    mm = Map()
    mm.add(vari_var.get(), data, "china")
    mm.set_global_opts(title_opts=opts.TitleOpts(title=month_var.get()),
                       visualmap_opts=opts.VisualMapOpts(max_=max,min_=min),
    )
    mm.render("map.html")
    a = '"C:/Program Files/Internet Explorer/iexplore.exe" '  + os.getcwd() + '\map.html'
    os.system(a)

tk.Button(frm_month, text='选择时间段', width=15,
              height=2, command=get_month).pack()



window.mainloop()