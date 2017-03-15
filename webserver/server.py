# -*- coding: utf-8 -*-


# package imports
import sqlite3
import json
import cherrypy
import time
import threading
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))


#local imports
import config
# cpu imports
from statsys import _cpu_thread, drop_create_cpu
from statsys import sql_select_cpu
# mem imports
from statsys import _mem_thread, drop_create_mem
from statsys import sql_select_mem
# swap imports
from statsys import _swap_thread, drop_create_swap
from statsys import sql_select_swap
# disk imports
from statsys import _disk_usage_home_thread, drop_create_disk_usage_home
from statsys import sql_select_disk_usage_home
from statsys import _disk_usage_root_thread, drop_create_disk_usage_root
from statsys import sql_select_disk_usage_root


class Application(object):
    @staticmethod
    def load_template(template, context):
        tmpl = env.get_template(template)
        return tmpl.render(**context)
        
    @cherrypy.expose
    def index(self):
        template = "base.html"
        context = {}
        return self.load_template(template, context)
    
    @cherrypy.expose
    def graph(self):
        template = "graph.html"
        context = {}
        return self.load_template(template, context)


class Data_JSON(object):
    @staticmethod
    def format_cpu(cpu_data, max_length=25):
        graph_data = [{'name': 'cpu0', 'x': [], 'y': [], 'mode': 'lines+markers', 'line': {'shape': 'spline'},},
                      {'name': 'cpu1', 'x': [], 'y': [], 'mode': 'lines+markers', 'line': {'shape': 'spline'},}, 
                      {'name': 'cpu2', 'x': [], 'y': [], 'mode': 'lines+markers', 'line': {'shape': 'spline'},}, 
                      {'name': 'cpu3', 'x': [], 'y': [], 'mode': 'lines+markers', 'line': {'shape': 'spline'},},
                      {'name': 'cpu4', 'x': [], 'y': [], 'mode': 'lines+markers', 'line': {'shape': 'spline'},},
                      {'name': 'cpu5', 'x': [], 'y': [], 'mode': 'lines+markers', 'line': {'shape': 'spline'},},
                      {'name': 'cpu6', 'x': [], 'y': [], 'mode': 'lines+markers', 'line': {'shape': 'spline'},},
                      {'name': 'cpu7', 'x': [], 'y': [], 'mode': 'lines+markers', 'line': {'shape': 'spline'},}]

        for num, row in enumerate(cpu_data):
            # exit at 30 rows max
            if num >= max_length:
                break

            for i, graph_row in enumerate(graph_data):
                graph_row['y'].append(row[i+1]) 
                graph_row['x'].append(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(row[0])))

        return graph_data

    @staticmethod
    def format_mem(mem_data, max_length=25):
        graph_data = {#{'name': 'total', 'x': [], 'y': [], 'type': 'bar'},
                      #{'name': 'available', 'x': [], 'y': [], 'type': 'bar'}, 
                      #{'name': 'percent', 'x': [], 'y': [], 'type': 'bar'}, 
                      'used': {'name': 'used', 'x': [], 'y': [], 'type': 'bar', 'marker': {'color': '#FF5353'}},#, 'text': []}, #, 'fill': 'tozeroy', 'mode': 'none'},
                      'free': {'name': 'free', 'x': [], 'y': [], 'type': 'bar', 'marker': {'color': '#0AFE47'}},#, 'text': []}, #, 'fill': 'tozeroy', 'mode': 'none'},
                      #'active': {'name': 'active', 'x': [], 'y': [], 'type': 'bar'},
                      #'inactive': {'name': 'inactive', 'x': [], 'y': [], 'type': 'bar'},
                      'buffers': {'name': 'buffers', 'x': [], 'y': [], 'type': 'bar', 'marker': {'color': '#F7DE00'}},#, 'text': []}, #, 'fill': 'tozeroy', 'mode': 'none'},
                      'cached': {'name': 'cached', 'x': [], 'y': [], 'type': 'bar', 'marker': {'color': '#2F74D0'}},#, 'text': []}, #, 'fill': 'tozeroy', 'mode': 'none'},
                      #'shared': {'name': 'shared', 'x': [], 'y': [], 'type': 'bar'}
                      }
        
        series_names = ['used',
                        'free',
                        #'active',
                        #'inactive',
                        'buffers',
                        'cached',
                        #'shared'
                        ]

        for num, row in enumerate(mem_data):
            # exit at 30 rows max
            if num >= max_length:
                break

            for name, val in row.items():
                if name in series_names:
                    graph_data[name]['x'].append(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(row['time']))) #'%X %p'
                    graph_data[name]['y'].append(row[name])
            
            ## used, used+cache, used+cache+buffers, used+cache+buffers+free
            #for name, series in graph_data.items():
                #if name == 'cached':
                    #graph_data[name]['y'][-1] = graph_data[name]['y'][-1] + graph_data['used']['y'][-1]
                
                #elif name == 'buffers':
                    #graph_data[name]['y'][-1] = graph_data[name]['y'][-1] + graph_data['cached']['y'][-1] + graph_data['used']['y'][-1]
                
                #elif name == 'free':
                    #graph_data[name]['y'][-1] = graph_data[name]['y'][-1] + graph_data['buffers']['y'][-1] + graph_data['cached']['y'][-1] + graph_data['used']['y'][-1]                
            
            #reduce number to GB
            for name in series_names:
                f_val = float(float(float(graph_data[name]['y'][-1]) / 1024) / 1024) / 1024
                graph_data[name]['y'][-1] = f_val #"{0:.2f}".format(f_val)
                #graph_data[name]['text'].append("GBytes")
            
            ret = [graph_data['used'],
                   graph_data['cached'],
                   graph_data['buffers'],
                   graph_data['free']]

        return ret

    @staticmethod
    def format_swap(swap_data, max_length=25):
        graph_data = {'used': {'name': 'used', 'x': [], 'y': [], 'type': 'bar', 'marker': {'color': '#FF5353'}},
                      'free': {'name': 'free', 'x': [], 'y': [], 'type': 'bar', 'marker': {'color': '#0AFE47'}},}
    
        series_names = ['used',
                        'free']
    
        for num, row in enumerate(swap_data):
            # exit at 30 rows max
            if num >= max_length:
                break
    
            for name, val in row.items():
                if name in series_names:
                    graph_data[name]['x'].append(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(row['time']))) #'%X %p'
                    graph_data[name]['y'].append(row[name])
    
            #reduce number to GB
            for name in series_names:
                f_val = float(float(float(graph_data[name]['y'][-1]) / 1024) / 1024) / 1024
                graph_data[name]['y'][-1] = f_val
    
            ret = [graph_data['used'],
                       graph_data['free']]
    
        return ret

    @staticmethod
    def format_disk_usage_home(disk_usage_home_data, max_length=25):
        graph_data = {'values': [],
                      'labels': [],
                      'type': 'pie'}
        
        graph_data['labels'].append('used')
        graph_data['values'].append(disk_usage_home_data[0]['used'])
        
        graph_data['labels'].append('free')
        graph_data['values'].append(disk_usage_home_data[0]['free'])
        
        return [graph_data]

    @staticmethod
    def format_disk_usage_root(disk_usage_root_data, max_length=25):
        graph_data = {'values': [],
                      'labels': [],
                      'type': 'pie'}
        
        graph_data['labels'].append('used')
        graph_data['values'].append(disk_usage_root_data[0]['used'] / 1024 / 1024 / 1024)
        
        graph_data['labels'].append('free')
        graph_data['values'].append(disk_usage_root_data[0]['free'] / 1024 / 1024 / 1024)
        
        return [graph_data]

    @cherrypy.expose
    def cpu(self):
        with sqlite3.connect("test.db") as con:
            cursor = con.cursor()
            cursor.execute(sql_select_cpu)
            data = tuple(cursor.fetchall())
            #print(data)
            formatted_data = json.dumps(self.format_cpu(data, 50))
            return formatted_data
    
    @cherrypy.expose
    def mem(self):
        with sqlite3.connect("test.db") as con:
            con.row_factory = dict_factory
            cursor = con.cursor()
            cursor.execute(sql_select_mem)
            data = tuple(cursor.fetchall())
            #print(data)
            formatted_data = json.dumps(self.format_mem(data, 100))
            return formatted_data    

    @cherrypy.expose
    def swap(self):
        with sqlite3.connect("test.db") as con:
            con.row_factory = dict_factory
            cursor = con.cursor()
            cursor.execute(sql_select_swap)
            data = tuple(cursor.fetchall())
            formatted_data = json.dumps(self.format_swap(data, 100))
            return formatted_data   

    @cherrypy.expose
    def disk_usage_home(self):
        with sqlite3.connect("test.db") as con:
            con.row_factory = dict_factory
            cursor = con.cursor()
            cursor.execute(sql_select_disk_usage_home)
            data = tuple(cursor.fetchall())
            formatted_data = json.dumps(self.format_disk_usage_home(data, 100))
            return formatted_data   

    @cherrypy.expose
    def disk_usage_root(self):
        with sqlite3.connect("test.db") as con:
            con.row_factory = dict_factory
            cursor = con.cursor()
            cursor.execute(sql_select_disk_usage_root)
            data = tuple(cursor.fetchall())
            formatted_data = json.dumps(self.format_disk_usage_root(data, 100))
            return formatted_data  

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


if __name__ == '__main__':

    cherrypy.config.update(config.config)
    
    # start cpu daemon
    drop_create_cpu()
    cpu_interval = 2
    cpu_thread = threading.Thread(target=_cpu_thread, args=(cpu_interval,))
    cpu_thread.start()
    
    # start mem daemon
    drop_create_mem()
    mem_interval = 2
    mem_thread = threading.Thread(target=_mem_thread, args=(mem_interval,))
    mem_thread.start()    

    # start swap daemon
    drop_create_swap()
    swap_interval = 2
    swap_thread = threading.Thread(target=_swap_thread, args=(swap_interval,))
    swap_thread.start()

    # start disk usage home daemon
    drop_create_disk_usage_home()
    disk_usage_home_interval = 2
    disk_usage_home_thread = threading.Thread(target=_disk_usage_home_thread, args=(disk_usage_home_interval,))
    disk_usage_home_thread.start()

    # start disk usage root daemon
    drop_create_disk_usage_root()
    disk_usage_root_interval = 2
    disk_usage_root_thread = threading.Thread(target=_disk_usage_root_thread, args=(disk_usage_root_interval,))
    disk_usage_root_thread.start()

    cherrypy.tree.mount(Application(), '/')
    cherrypy.tree.mount(Data_JSON(), '/json')

    cherrypy.engine.start()
    cherrypy.engine.block()
    