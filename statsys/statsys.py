import psutil
import time
import sys
import sqlite3

database = "./test.db"

sql_drop_cpu = """
DROP TABLE IF EXISTS cpu
"""

sql_create_cpu = """
CREATE TABLE IF NOT EXISTS cpu (id ID, 
                                time FLOAT, cpu0 FLOAT, cpu1 FLOAT, 
                                cpu2 FLOAT, cpu3 FLOAT, cpu4 FLOAT
                                cpu5 FLOAT, cpu6 FLOAT, cpu7 FLOAT)
"""

sql_insert_cpu = """
INSERT INTO cpu VALUES (?, ?, ?,
                        ?, ?, ?,
                        ?, ?, ?)
"""

sql_select_cpu = """
SELECT *
  FROM cpu
"""

# cehck cpu defs
def check_cpu(interval=1, multi_cpu=True):
    ret = [time.time(), *psutil.cpu_percent(interval=interval, percpu=multi_cpu)]
    return ret

def _cpu_thread(refresh_interval=1):
    while True:
        data = check_cpu(interval=None)
        update_db(sql_insert_cpu, data)
        time.sleep(1)

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


if __name__ == "__main__":
    
    import time
    start = time.time()
    
    # create table for cpu data
    run_sql(sql_drop_cpu)
    run_sql(sql_create_cpu)
    
    # start cpu_daemon
    import threading
    cpu_interval = 1
    t = threading.Thread(target=_cpu_thread, args=(cpu_interval,))
    t.start()
    
    while True:
        for row in run_select(sql_select_cpu):
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