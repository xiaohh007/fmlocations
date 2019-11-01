import datetime

from numba import none

from MysqlHelp import DB

if __name__ == '__main__':
# out = '89.5'
# global radiovaluelist
#
# locationvaluelists = []
# with DB(host='47.92.33.19',user='root',passwd='1qazxsw2',db='database_fm') as db:
#     db.execute("select frequency,fmcoding,lng ,lat FROM fm_t_fmlocation WHERE frequency='{}' ".format(float(out)))
#     locationlist = db.fetchall()
#
# for location in locationlist:
#
#     locationvaluelist = list(location.values())
#
#     locationvaluelists.append(locationvaluelist)
#
#
# print(locationvaluelists)
    import countour_predict_value as cpv
    from geopy.distance import geodesic



    result = cpv.pred_location('90.9', '2019-10-31 00:00:00', '2019-11-01 16:36:00')

    print(geodesic((result[2], result[1]), (31.244937,121.506373)).m) #计算两个坐标直线距离
    print(geodesic((31.30169546322556,121.38089409658731), (30.96444862415061,121.15025151332885)).km) #计算两个坐标直线距离


# coding = 'asdfl;lk;kk'
# print(coding[-1])