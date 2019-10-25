import datetime

import schedule
from geopy.distance import geodesic
from numba import none
from numpy import double

import countour_predict_value as cpv
from MysqlHelp import DB



def five_minutes():
    endtime = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
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

        radiolist = query_radiolist(out)
        print("radiolist++++++++++++++",radiolist)

        print(result_accuratetype)
        result_facility_list = ",".join(result[3])
        serialnumber = 1
        print(result_lng)
        print(result_lat)
        print(type(result_lng))
        print(type(result_lat))
        print(frequency)


        if result_lat is not None and 30.0 <= result_lat <= 32.0:

            if result_lng is not None and result_lng > 100.0:

                if out in codingfrequencylist:


                    with DB(host='47.92.33.19',user='root',passwd='1qazxsw2',db='database_fm') as db:
                        db.execute("UPDATE fm_t_fmlocation SET lng = '{}' , lat = '{}' WHERE frequency = '{}' "
                                   .format(result_lng,result_lat,result_frequency))
                        print("该频率已存在,更新数据!")
                    # if len(radiolist) > 0 and radiolist[2] is not None :
                    #
                    #         radio_lng = radiolist[3]
                    #         radio_lat = radiolist[4]
                    #         radio_createtime = radiolist[1]
                    #         radio_fmcoding = radiolist[2]
                    #         radio_bantime = radiolist[5]
                    #         coding = int(radio_fmcoding[-1])
                    #         distance_fm = error_range(radio_lng,radio_lat,result_lng,result_lat)
                    #         if radio_bantime is None:
                    #             if distance_fm > 20000:
                    #                 fmcoding = str(result_frequency+"_"+str(endtime).replace('-','').replace(':','').replace(' ',''))
                    #                 fmcoding = fmcoding+'_'+str(coding + 1)
                    #                 with DB(host='47.92.33.19',user='root',passwd='1qazxsw2',db='database_fm') as db:
                    #                     db.execute("INSERT into fm_t_fmlocation (id,time,size,frequency,lng,lat,fmcoding,equipmentschedule,status,positioning_level) VALUES(null,'{}',5,'{}','{}','{}','{}','{}','new','{}')"
                    #                                .format(endtime,result_frequency,result_lng,result_lat,fmcoding,result_facility_list,result_accuratetype))
                    #
                    #             else:
                    #                 fmcoding = str(result_frequency+"_"+str(radio_createtime).replace('-','').replace(':','').replace(' ',''))
                    #                 with DB(host='47.92.33.19',user='root',passwd='1qazxsw2',db='database_fm') as db:
                    #                     db.execute("UPDATE fm_t_fmlocation SET lng = '{}' , lat = '{}',fmcoding = '{}', positioning_level ='{}' WHERE fmcoding = '{}' and positioning_level > '{}'"
                    #                                .format(result_lng,result_lat,radio_fmcoding,result_accuratetype,radio_fmcoding,result_accuratetype))
                    #
                    #         else:
                    #             fmcoding = str(result_frequency+"_"+str(endtime).replace('-','').replace(':','').replace(' ',''))
                    #             fmcoding = fmcoding+'_'+str(coding + 1)
                    #             with DB(host='47.92.33.19',user='root',passwd='1qazxsw2',db='database_fm') as db:
                    #                 db.execute("INSERT into fm_t_fmlocation (id,time,size,frequency,lng,lat,fmcoding,equipmentschedule,status,positioning_level) VALUES(null,'{}',5,'{}','{}','{}','{}','{}','new','{}')"
                    #                            .format(endtime,result_frequency,result_lng,result_lat,fmcoding,result_facility_list,result_accuratetype))
                    # else:
                    #
                    #     locationvaluelists = query_fmlocation(out)
                    #
                    #     locations_lng = locationvaluelists[2]
                    #     locations_lat = locationvaluelists[3]
                    #     locations_fmcoding = locationvaluelists[1]
                    #     coding = int(locations_fmcoding[-1])
                    #     distance_fm = error_range(locations_lng,locations_lat,result_lng,result_lat)
                    #     if distance_fm > 20000:
                    #         fmcoding = str(result_frequency+"_"+str(endtime).replace('-','').replace(':','').replace(' ',''))
                    #         fmcoding = fmcoding+'_'+str(coding + 1)
                    #         with DB(host='47.92.33.19',user='root',passwd='1qazxsw2',db='database_fm') as db:
                    #             db.execute("INSERT into fm_t_fmlocation (id,time,size,frequency,lng,lat,fmcoding,equipmentschedule,status,positioning_level) VALUES(null,'{}',5,'{}','{}','{}','{}','{}','new','{}')"
                    #                        .format(endtime,result_frequency,result_lng,result_lat,fmcoding,result_facility_list,result_accuratetype))
                    #     else:
                    #         print("该频率信息已存在!")

                else:
                    fmcoding = str(result_frequency+"_"+str(endtime).replace('-','').replace(':','').replace(' ',''))
                    fmcoding = fmcoding+'_'+str(serialnumber)
                    with DB(host='47.92.33.19',user='root',passwd='1qazxsw2',db='database_fm') as db:
                        db.execute("INSERT into fm_t_fmlocation (id,time,size,frequency,lng,lat,fmcoding,equipmentschedule,positioning_level) VALUES(null,'{}',5,'{}','{}','{}','{}','{}','{}')"
                           .format(endtime,result_frequency,result_lng,result_lat,fmcoding,result_facility_list,result_accuratetype))

            else:
                print("数据计算有误,不保存数据")
                continue


        else:
            print("数据计算有误,不保存数据")
            continue

def query_radiolist(out):
    global radiovaluelist
    print('query_radiolist++++++++++++++++',out)
    radiovaluelist = []
    with DB(host='47.92.33.19',user='root',passwd='1qazxsw2',db='database_fm') as db:
        db.execute("select frequency,create_time,fmcoding,lng ,lat,ban_time FROM fm_t_radiolist WHERE frequency='{}' order by id desc limit 1".format(float(out)))
        radiolist = db.fetchall()

    for radio in radiolist:
        print(radio)
        radiovaluelist = list(radio.values())
    return radiovaluelist


def query_fmlocation(out):
    global locationvaluelist
    locationvaluelist = []
    outfrequency= float(out)
    with DB(host='47.92.33.19',user='root',passwd='1qazxsw2',db='database_fm') as db:
        db.execute("select frequency,fmcoding,lng ,lat FROM fm_t_fmlocation WHERE frequency='{}' order by id desc limit 1".format(outfrequency))
    locationlist = db.fetchall()

    for location in locationlist:
        print(location)
        locationvaluelist = list(location.values())
    return locationvaluelist

def error_range(radio_lng,radio_lat,result_lng,result_lat):
    distance_fm = geodesic((radio_lat,radio_lng), (result_lat,result_lng)).m
    return distance_fm

if __name__ == '__main__':

    global endtime



    # schedule.every(5).seconds.do(job1)
    schedule.every(300).seconds.do(five_minutes)
    # schedule.every(50).seconds.do(thirty_minutes)
    # schedule.every(500).seconds.do(one_day)

    while True:
        schedule.run_pending()