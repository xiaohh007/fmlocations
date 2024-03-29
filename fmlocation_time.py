import datetime

import schedule
from numba import none
from numpy import double

import countour_predict_value as cpv
from MysqlHelp import DB



def five_minutes():
    starttime = (datetime.datetime.now()+datetime.timedelta(hours= -3)).strftime("%Y-%m-%d %H:%M:%S")
    print(starttime)
    with DB(host='47.92.33.19',user='root',passwd='1qazxsw2',db='database_fm') as db:
        db.execute("SELECT distinct frequency FROM fm_t_scan_record where upload_time BETWEEN date_add(now(), interval - 5 minute) and now() ")
        frequencylist = db.fetchall()
        print(frequencylist)
    # with DB(host='47.92.33.19',user='root',passwd='1qazxsw2',db='database_fm') as db:
        db.execute("SELECT distinct frequency FROM fm_t_fmlocation ")
        codingfrequencydict = db.fetchall()
        codingfrequencylist = []
    for codingfrequency in codingfrequencydict:
        str_codingfrequency = list(codingfrequency.values())
        out = str(str_codingfrequency).replace('[','').replace(']','')
        codingfrequencylist.append(out)
    print(codingfrequencylist)


    for frequency in frequencylist:
        str_frequency = list(frequency.values())
        out = str(str_frequency).replace('[','').replace(']','')
        print(out)
        result = cpv.pred_location( out , starttime, endtime)
        result_frequency = result[0]
        result_lng = result[1]
        result_lat = result[2]
        result_accuratetype = str(result[4])
        print(result_accuratetype)
        result_facility_list = ",".join(result[3])
        fmcoding = str(result_frequency+"_"+str(endtime).replace('-','').replace(':','').replace(' ','')+"_"+result_accuratetype)
        print(result_lng)
        print(result_lat)
        print(type(result_lng))
        print(type(result_lat))
        print(type(frequency))


        if result_lat is not None and 30.0 <= result_lat <= 32.0:
            if result_lng is not None and result_lng > 100.0:

                if out in codingfrequencylist:
                    fmcoding = fmcoding+"_001"
                    with DB(host='47.92.33.19',user='root',passwd='1qazxsw2',db='database_fm') as db:
                        db.execute("INSERT into fm_t_fmlocation (id,time,size,frequency,lng,lat,fmcoding,equipmentschedule,status,positioning_level) VALUES(null,'{}',5,'{}','{}','{}','{}','{}','old','{}')"
                                   .format(endtime,result_frequency,result_lng,result_lat,fmcoding,result_facility_list,result_accuratetype))
                else:
                    fmcoding = fmcoding+"_000"
                    with DB(host='47.92.33.19',user='root',passwd='1qazxsw2',db='database_fm') as db:
                        db.execute("INSERT into fm_t_fmlocation (id,time,size,frequency,lng,lat,fmcoding,equipmentschedule,status,positioning_level) VALUES(null,'{}',5,'{}','{}','{}','{}','{}','new','{}')"
                           .format(endtime,result_frequency,result_lng,result_lat,fmcoding,result_facility_list,result_accuratetype))

            else:
                print("数据计算有误,不保存数据")
                continue


        else:
            print("数据计算有误,不保存数据")
            continue









    # def thirty_minutes(start,end):
#
#
# def one_day(start,end):


if __name__ == '__main__':

    global endtime
    endtime = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


    # schedule.every(5).seconds.do(job1)
    schedule.every(10).seconds.do(five_minutes)
    # schedule.every(1500).seconds.do(thirty_minutes(start))
    # schedule.every(86400).seconds.do(one_day(start))

    while True:
        schedule.run_pending()