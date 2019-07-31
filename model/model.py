
#定义数据库操作
from config import db_conn

# rec_msg_dict.update({
#     'msg_id': msg_id,
#     'msg_from_user': msg_from_user,  # 发消息的用户 id
#     'msg_rec_user': msg_rec_user,
#     'msg_time_rec': msg_time_rec,
#     'msg_type': msg_type,
#     'msg_content': msg_content,
#     'msg_from_user_name': msg_from_user_name,  # 发消息用户 id
#     'msg_rec_user_name': msg_rec_user_name,
#     'msg_group': msg_group,  # 群聊 id
#     'msg_group_name': msg_group_name,  # 群聊名称
# })
mydb = db_conn()

class wxrobot:
    msg_id = ''
    msg_type = ''
    msg_time = ''
    msg_content = ''
    msg_sender = ''
    msg_receiver = ''
    msg_sender_name = ''
    msg_receiver_name = ''
    is_at = 0
    is_group = 0
    msg_group = ''
    msg_group_name = ''
    def __init__(self,msg_id,type,time,content,sender,receiver,sender_name,receiver_name,is_at,is_group,group,group_name):
        self.msg_id = msg_id
        self.msg_type = type
        self.msg_time = time
        self.msg_content = content
        self.msg_sender = sender
        self.msg_receiver = receiver
        self.msg_sender_name = sender_name
        self.msg_receiver_name = receiver_name
        self.is_at = is_at
        self.is_group = is_group
        self.msg_group = group
        self.msg_group_name = group_name

    def insert_db(self):
        sql = "INSERT INTO wxrobot (msg_id,msg_type,msg_time,msg_content,msg_sender,msg_receiver,msg_sender_name,msg_receiver_name,is_at,is_group,msg_group,msg_group_name) VALUES (%s, %s, %s,%s, %s,%s, %s,%s, %s, %s,%s, %s)"
        val = (self.msg_id,self.msg_type, self.msg_time,self.msg_content,self.msg_sender,self.msg_receiver,self.msg_sender_name,self.msg_receiver_name,self.is_at,self.is_group,self.msg_group,self.msg_group_name)
        mydb.ping(reconnect=True)
        self.mycursor = mydb.cursor()
        try:
            self.mycursor.execute(sql, val)
            mydb.commit()
        except Exception as e:
            content = self.msg_content[:2]
            qunname = str(self.msg_group_name.encode('utf-8'))
            val = (
            self.msg_id, self.msg_type, self.msg_time, content, self.msg_sender, self.msg_receiver, self.msg_sender_name, self.msg_receiver_name, self.is_at,
            self.is_group, self.msg_group, qunname)
            self.mycursor.execute(sql, val)
            mydb.commit()
            print('警告,可能是消息中的特殊字符导致', e)
        finally:
            self.mycursor.close()
        return 

#把数据处理，存入统计表
class Statistical(object):
    def __init__(self, deal_rep):
        self.mydb = mydb    #数据库
        self.msg_id = deal_rep['msg_id']
        self.content = deal_rep['msg_content']  #正文
        self.msg_time = deal_rep['msg_time_rec']    #2019-06-16 17:08:50
        self.msg_from_user = deal_rep['msg_from_user']  #用户id
        self.msg_user_nickname = deal_rep['msg_user_nickname']  #用户昵称
        self.msg_group_name = deal_rep['msg_from_user_name']    #群聊名称

    def dbselect(self):
        msg_date = self.msg_time.split(' ')[0]  #消息的日期

        # sql = 'select * from %s where msg_sender=%s' % ('statisticstask', self.msg_from_user)
        sql = "select max(msg_time) from statisticstask where msg_sender_name=%s"
        val = (self.msg_user_nickname)
        cursor = self.mydb.cursor()
        cursor.execute(sql, val)
        res = cursor.fetchone()[0] #获取所有条目
        cursor.close()
        if res:
            res_data = res.strftime('%Y-%m-%d')  #数据库存储的相关用户最后日期
            if msg_date > res_data:
                return True     #可以存储数据
            else:
                return False    #数据库已经保存，不再进行存储
        else:   #未查到条目说明刚开始打卡，数据库还没有他的值
            return True

    def save_sql(self):
        '''存入数据库'''
        #is_save 字段保存为打卡
        sql = 'insert into statisticstask (msg_id, msg_time,msg_sender,msg_sender_name,msg_content,msg_group_name,is_save) value (%s,%s,%s,%s,%s,%s, TRUE)'
        val = (self.msg_id, self.msg_time, self.msg_from_user, self.msg_user_nickname, self.content,self.msg_group_name)
        self.mydb.ping(reconnect=True)
        cursor = self.mydb.cursor()
        try:
            cursor.execute(sql,val)
            self.mydb.commit()
            return True
        except Exception as e:
            print('插入出错', e)
            return False
        finally:
            cursor.close()

    def saveuseinfo(self):
        if self.dbselect():
            res = self.save_sql()
            return res
        else:
            return 'issaved'

def getresult():
    #获取本月的打卡数据
    sql = "select msg_sender_name,count(is_save) from statisticstask where DATE_FORMAT(msg_time,'%Y%m') = DATE_FORMAT(CURDATE(), '%Y%m') group by msg_sender_name"
    mydb.ping(reconnect=True)
    cursor = mydb.cursor()
    try:
        cursor.execute(sql)
        res = cursor.fetchall()
        print(res)

        msg = '本月打卡信息统计：'+'\n'+'昵称'+'\t' + '打卡次数' + '\n'
        namecount = ''
        for name,count in res:
            print(name, count)
            namecount += name + '\t' + str(count) + '\n'
        rescount = msg + namecount + '\n' + '加油，更自律更自由[强]'
        return rescount
    except Exception as e:
        msgerr = '错误：' + str(e)
        return msgerr
    finally:
        cursor.close()
