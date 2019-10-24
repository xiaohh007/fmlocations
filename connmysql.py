# -*- coding: utf-8 -*-
# 导入pymysql模块
import pymysql

import pandas as pd 
import numpy as np 
def get_fmdata(fm, starttime, endtime):
    # 连接database
    conn = pymysql.connect(host="47.92.33.19", user="root",password="1qazxsw2",database="database_fm",charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    # 定义要执行的SQL语句
    # sql = """select a.id,b.device_lgid,a.frequency,a.lon,a.lat,a.signal_strength,c.area,d.lon,d.lat,DATE_FORMAT(a.upload_time,'%Y-%c-%d %H:%i:%S') AS upload_time from fm_t_scan_record a
    # LEFT JOIN fm_t_task_record b ON a.task_record_id = b.id 
    # LEFT JOIN fm_t_whitelist c ON a.frequency = c.frequency 
    # LEFT JOIN fm_t_address d ON c.area = d.name where upload_time > DATE_SUB(NOW(),INTERVAL  0.5 HOUR) ORDER BY a.frequency"""

    # sql = """select a.id, b.device_lgid,a.frequency,a.lon,a.lat,a.signal_strength,c.area,d.lon,d.lat,DATE_FORMAT(a.upload_time,'%Y-%c-%d %H:%i:%S') AS upload_time from fm_t_scan_record a
    # LEFT JOIN fm_t_task_record b ON a.task_record_id = b.id 
    # LEFT JOIN fm_t_whitelist c ON a.frequency = c.frequency 
    # LEFT JOIN fm_t_address d ON c.area = d.name where upload_time > DATE_SUB(NOW(),INTERVAL 30 MINUTE) order by a.frequency"""

    # sql = """select a.id, b.device_lgid,a.frequency,a.lon,a.lat,a.signal_strength,c.area,d.lon,d.lat,DATE_FORMAT(a.upload_time,'%Y-%c-%d %H:%i:%S') AS upload_time from fm_t_scan_record a
    # LEFT JOIN fm_t_task_record b ON a.task_record_id = b.id 
    # LEFT JOIN fm_t_whitelist c ON a.frequency = c.frequency 
    # LEFT JOIN fm_t_address d ON c.area = d.name where (a.frequency = 87.9) AND upload_time > DATE_SUB(NOW(),INTERVAL 0.5 HOUR)  """
    # 执行SQL语句96.2  95.9 87.9 107.7  98.1  91.4  89.9 93.4  a.frequency = '87.9' AND 

    # sql = '''select a.id, b.device_lgid,a.frequency,a.lon,a.lat,a.signal_strength,c.area,d.lon,d.lat,DATE_FORMAT(a.upload_time,'%Y-%c-%d %H:%i:%S') AS upload_time from fm_t_scan_record a
    # LEFT JOIN fm_t_task_record b ON a.task_record_id = b.id 
    # LEFT JOIN fm_t_whitelist c ON a.frequency = c.frequency 
    # LEFT JOIN fm_t_address d ON c.area = d.name where a.frequency ='''+ fm +''' AND DATE_FORMAT(a.upload_time,'%Y-%c-%d %H:%i:%S') BETWEEN \''''+ starttime + '''\' AND \''''+ endtime+ '''\' ORDER BY a.frequency'''


    sql = '''SELECT a.id, b.device_lgid,a.frequency,a.lon,a.lat,a.signal_strength,c.area,d.lon,d.lat,DATE_FORMAT(a.upload_time,'%Y-%c-%d %H:%i:%S') AS upload_time FROM fm_t_scan_record a
    LEFT JOIN fm_t_task_record b ON a.task_record_id = b.id 
    LEFT JOIN fm_t_whitelist c ON a.frequency = c.frequency 
    LEFT JOIN fm_t_address d ON c.area = d.name where a.frequency ='''+ fm +''' AND DATE_FORMAT(a.upload_time,'%Y-%c-%d %H:%i:%S') BETWEEN \''''+ starttime + '''\' AND \''''+ endtime+ '''\' ORDER BY a.frequency'''


    try:
        cursor.execute(sql)
        # 关闭光标对象
        sql_result = cursor.fetchall()
    except Exception as ex:
        raise ex
    finally:
        cursor.close()
        # 关闭数据库连接
        conn.close()

    re = pd.DataFrame(np.resize(sql_result,(len(sql_result),10)), columns=['id','deviceid','fm','lon','lat','db','local','fmlon','fmlat','time'])
    return re

def get_fmtdevice():
    # 连接database
    conn = pymysql.connect(host="47.92.33.19", user="root",password="1qazxsw2",database="database_fm",charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()

    sql = '''SELECT phy_id,lon,lat FROM fm_t_device'''

  
    try:
        cursor.execute(sql)
        # 关闭光标对象
        sql_result = cursor.fetchall()
    except Exception as ex:
        raise ex
    finally:
        cursor.close()
        # 关闭数据库连接
        conn.close()

    re = pd.DataFrame(np.resize(sql_result,(len(sql_result),3)), columns=['deviceid','lon','lat'])
    return re