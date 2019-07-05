
#定义数据库与其他字段的初始值配置文件
import pymysql
import os


def db_conn():

    mydb = pymysql.connect(
        host="127.0.0.1",       # 数据库主机地址
        user="root",    # 数据库用户名
        passwd="xxxxxx",   # 数据库密码
        database="wxrobot",  # 数据库
    )
    return mydb
mydb = db_conn()

akikey = '688f985db1644ceab097f1987959986e'
KEY = '686c5523361f9154'



rec_tmp_dir = os.path.join(os.getcwd(), 'mediafile/')

groupnames = ['测试群聊', '测试群聊2号' ]        #你要监控的群聊名称,消息存储
