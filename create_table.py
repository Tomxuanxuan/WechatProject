from config import mydb

#创建消息数据表
def create_table():
    sql = '''create table wxrobot(
        msg_id varchar(50),
        msg_type char(20),
        msg_time Datetime,
        msg_content varchar(255),
        msg_sender  varchar(255),
        msg_receiver  varchar(255),
        msg_sender_name  varchar(255),
        msg_receiver_name  varchar(255),
        is_at  BOOLEAN,
        is_group  BOOLEAN,
        msg_group varchar(255),
        msg_group_name varchar(255)
    )'''
    try:
        cursor = mydb.cursor()
        cursor.execute(sql)
        mydb.commit()
        print('创建成功')
        return True
    except Exception as e:
        print('创建失败', e)
        return False
    finally:
        cursor.close()

#创建打卡数据表
def statisticstask():
    sql = '''create table statisticstask(
        msg_id varchar(50),
        msg_type char(20),
        msg_time Datetime,
        msg_content varchar(255),
        msg_sender  varchar(255),
        msg_receiver  varchar(255),
        msg_sender_name  varchar(255),
        msg_receiver_name  varchar(255),
        is_at  BOOLEAN,
        is_group  BOOLEAN,
        msg_group varchar(255),
        msg_group_name varchar(255),
        is_save BOOLEAN
    )'''
    try:
        cursor = mydb.cursor()
        cursor.execute(sql)
        mydb.commit()
        print('创建成功')
        return True
    except Exception as e:
        print('创建失败', e)
        return False
    finally:
        cursor.close()

create_table()
statisticstask()
