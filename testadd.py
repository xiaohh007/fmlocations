import datetime

from MysqlHelp import DB


out = '107.2'
with DB(host='47.92.33.19',user='root',passwd='1qazxsw2',db='database_fm') as db:
    db.execute("select frequency,create_time,fmcoding,lng ,lat FROM fm_t_radiolist WHERE frequency='{}'".format(out))
    radiolist = db.fetchall()

    for radio in radiolist:
        print(radio)
        radiovaluelist = list(radio.values())
        radio_frequency=[]
        radio_createtime=[]
        radio_fmcoding=[]
        radio_lng=[]
        radio_lat=[]
        radio_frequency.append(radiovaluelist[0])
        radio_createtime.append(radiovaluelist[1])
        radio_fmcoding.append(radiovaluelist[2])
        radio_lng.append(radiovaluelist[3])
        radio_lat.append(radiovaluelist[4])

    print(radio_frequency)
    print(radio_createtime)
    print(radio_fmcoding)
    print(radio_lng)
    print(radio_lat)
