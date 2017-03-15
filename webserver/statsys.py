import psutil
import time
import sys
import sqlite3

database = "test.db"

sql_drop_cpu = """
DROP TABLE IF EXISTS cpu;
"""

sql_create_cpu = """
CREATE TABLE IF NOT EXISTS cpu (time FLOAT, cpu0 FLOAT, cpu1 FLOAT, 
                                cpu2 FLOAT, cpu3 FLOAT, cpu4 FLOAT,
                                cpu5 FLOAT, cpu6 FLOAT, cpu7 FLOAT);
"""

sql_insert_cpu = """
INSERT INTO cpu VALUES (?, ?, ?,
                        ?, ?, ?,
                        ?, ?, ?);
"""

sql_select_cpu = """
  SELECT *
    FROM cpu
ORDER BY time DESC;
"""

sql_drop_mem = """
DROP TABLE IF EXISTS mem;
"""

sql_create_mem = """
CREATE TABLE IF NOT EXISTS mem (time FLOAT, total INTEGER, available INTEGER, 
                                percent FLOAT, used INTEGER, free INTEGER, 
                                active INTEGER, inactive INTEGER, buffers INTEGER, 
                                cached INTEGER, shared INTEGER);
"""

sql_insert_mem = """
INSERT INTO mem VALUES (?, ?, ?,
                        ?, ?, ?,
                        ?, ?, ?,
                        ?, ?);
"""

sql_select_mem = """
  SELECT *
    FROM mem
ORDER BY time DESC;
"""

sql_drop_swap = """
DROP TABLE IF EXISTS swap;
"""

sql_create_swap = """
CREATE TABLE IF NOT EXISTS swap (time FLOAT, total INTEGER, used INTEGER, 
                                 free INTEGER, percent FLOAT, sin INTEGER, 
                                 sout INTEGER);
"""

sql_insert_swap = """
INSERT INTO swap VALUES (?, ?, ?,
                         ?, ?, ?,
                         ?);
"""

sql_select_swap = """
  SELECT *
    FROM swap
ORDER BY time DESC;
"""

sql_drop_disk_usage_home = """
DROP TABLE IF EXISTS disk_usage_home;
"""

sql_create_disk_usage_home = """
CREATE TABLE IF NOT EXISTS disk_usage_home (time FLOAT, total INTEGER, used INTEGER, 
                                            free INTEGER, percent FLOAT);
"""

sql_insert_disk_usage_home = """
INSERT INTO disk_usage_home VALUES (?, ?, ?,
                                    ?, ?);
"""

sql_select_disk_usage_home = """
  SELECT *
    FROM disk_usage_home
ORDER BY time DESC
   LIMIT 1;
"""

sql_drop_disk_usage_root = """
DROP TABLE IF EXISTS disk_usage_root;
"""

sql_create_disk_usage_root = """
CREATE TABLE IF NOT EXISTS disk_usage_root (time FLOAT, total INTEGER, used INTEGER, 
                                            free INTEGER, percent FLOAT);
"""

sql_insert_disk_usage_root = """
INSERT INTO disk_usage_root VALUES (?, ?, ?,
                                    ?, ?);
"""

sql_select_disk_usage_root = """
  SELECT *
    FROM disk_usage_root
ORDER BY time DESC
   LIMIT 1;
"""

# cehck cpu defs
def check_cpu(interval=1, multi_cpu=True):
    ret = [time.time(), *psutil.cpu_percent(interval=interval, percpu=multi_cpu)]
    return ret

def _cpu_thread(refresh_interval=1):
    while True:
        data = check_cpu(interval=None)
        update_db(sql_insert_cpu, data)
        time.sleep(refresh_interval)

# check ram defs
def check_mem():
    ret = [time.time(), *psutil.virtual_memory()]
    return ret

def _mem_thread(refresh_interval=1):
    while True:
        data = check_mem()
        update_db(sql_insert_mem, data)
        time.sleep(refresh_interval)

# check swap defs
def check_swap():
    ret = [time.time(), *psutil.swap_memory()]
    return ret

def _swap_thread(refresh_interval=1):
    while True:
        data = check_swap()
        update_db(sql_insert_swap, data)
        time.sleep(refresh_interval)

# check disk usage home defs
def check_disk_usage_home():
    ret = [time.time(), *psutil.disk_usage("/home")]
    return ret

def _disk_usage_home_thread(refresh_interval=1):
    while True:
        data = check_disk_usage_home()
        update_db(sql_insert_disk_usage_home, data)
        time.sleep(refresh_interval)

# check disk usage root defs
def check_disk_usage_root():
    ret = [time.time(), *psutil.disk_usage("/")]
    return ret

def _disk_usage_root_thread(refresh_interval=1):
    while True:
        data = check_disk_usage_root()
        update_db(sql_insert_disk_usage_root, data)
        time.sleep(refresh_interval)

# database defs
def update_db(sql, data):
    with sqlite3.connect(database) as con:
        cursor = con.cursor()
        cursor.execute(sql, data)
            
def run_sql(sql):
    with sqlite3.connect(database) as con:
        cursor = con.cursor()
        cursor.execute(sql)

def run_select(sql):
    with sqlite3.connect(database) as con:
        cursor = con.cursor()
        cursor.execute(sql)
        return cursor.fetchall()

def drop_create_cpu():
    # create table for cpu data
    print("dropping table cpu")
    run_sql(sql_drop_cpu)
    print("creating table cpu")
    run_sql(sql_create_cpu)

def drop_create_mem():
    # create table for cpu data
    print("dropping table mem")
    run_sql(sql_drop_mem)
    print("creating table mem")
    run_sql(sql_create_mem)

def drop_create_swap():
    # create table for cpu data
    print("dropping table swap")
    run_sql(sql_drop_swap)
    print("creating table swap")
    run_sql(sql_create_swap)

def drop_create_disk_usage_home():
    # create table for cpu data
    print("dropping table disk_usage_home")
    run_sql(sql_drop_disk_usage_home)
    print("creating table disk_usage_home")
    run_sql(sql_create_disk_usage_home)

def drop_create_disk_usage_root():
    # create table for cpu data
    print("dropping table disk_usage_root")
    run_sql(sql_drop_disk_usage_root)
    print("creating table disk_usage_root")
    run_sql(sql_create_disk_usage_root)

if __name__ == "__main__":
    
    import time
    start = time.time()
    
    # create table for cpu data
    run_sql(sql_drop_swap)
    run_sql(sql_create_swap)
    
    
    
    # start cpu_daemon
    import threading
    swap_interval = 1
    swap_thread = threading.Thread(target=_swap_thread, args=(swap_interval,))
    swap_thread.start()
    
    while True:
        for row in run_select(sql_select_swap):
            try:
                print("""    +-----------------------------------------------+
    | Time: {:10.7f}                      |
    | cpu0: {:2.2f} | cpu1: {:2.2f} | cpu2: {:2.2f} | cpu3: {:2.2f} |
    | cpu4: {:2.2f} | cpu5: {:2.2f} | cpu6: {:2.2f} | cpu7: {:2.2f} |
    +-----------------------------------------------+
    """.format(*row))
            except:
                pass
        time.sleep(5)
    
    print("Time elapsed: {}s".format(end-start))