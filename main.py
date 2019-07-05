
from config import db_conn, rec_tmp_dir,groupnames
import itchat
from itchat.content import *
import time
from model.model import wxrobot,Statistical,getresult
import os
import re

rec_msg_dict = {}
rec_group_dict = {} #群聊消息
face_bug = None #表情包内容
msg_information = {}    #处理撤回消息的字典
loadUser = {}   #登录用户信息
# 'UserName': '@8877ed05f155e792c87d3ea2a2f240a63afd579fb92916b7f1a22409c7b2bfea', 'City': '', 'DisplayName': '', 'PYQuanPin': '', 'RemarkPYInitial': '', 'Province': '', 'KeyWord': '', 'RemarkName': '', 'PYInitial': '', 'EncryChatRoomId': '', 'Alias': '', 'Signature': '我们的征途是星辰和大海', 'NickName': '心安', 'RemarkPYQuanPin': '', 'HeadImgUrl': '/cgi-bin/mmwebwx-bin/webwxgeticon?seq=83375339&username=@8877ed05f155e792c87d3ea2a2f240a63afd579fb92916b7f1a22409c7b2bfea&skey=@crypt_ce55c70d_608fa9782257d9b38e97b9259a92fd4e', 'UniFriend': 0, 'Sex': 1, 'AppAccountFlag': 0, 'VerifyFlag': 0, 'ChatRoomId': 0, 'HideInputBarFlag': 0, 'AttrStatus': 0, 'SnsFlag': 17, 'MemberCount': 0, 'OwnerUin': 0, 'ContactFlag': 0, 'Uin': 813635521, 'StarFriend': 0, 'Statues': 0, 'MemberList': [], 'WebWxPluginSwitch': 0, 'HeadImgFlag': 1}

#机器人登录成功
def after_login():
    print('微信robot登录成功')
    global mydb, loadUser
    mydb = db_conn()
    loadUser = itchat.search_friends()

#机器人退出登录
def after_logout():
    print('微信robot退出成功')
    mydb.close()

#接收到的好友消息处理
def deal_user_msg(msg):
    global face_bug
    msg_id = msg['MsgId']   #消息 id
    msg_from_user = msg['FromUserName']     #来源用户 id
    if msg_from_user == loadUser['UserName']:  # 是登录用户自己发的回复消息
        msg_from_user_name = loadUser['NickName']   #昵称是自己
    else:
        try:
            msg_from_user_name = msg['User']['NickName'] if u'NickName' in msg['User'] else msg['User']['UserName'] #来源用户昵称
        except:
            try:
                msg_from_user = itchat.search_friends(userName=msg['FromUserName'])
                if msg_from_user['RemarkName']:
                    msg_from_user_name = msg_from_user['RemarkName']
                else:
                    msg_from_user_name = msg_from_user['NickName']

            except:
                msg_from_user_name = '未知用户'
    msg_content = ''
    msg_time_rec = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    msg_type = msg['Type']  #消息类型

    msg_share_url = None

    if msg['Type'] == 'Text':
        msg_content = msg['Content']
    elif msg['Type'] == 'Picture' \
            or msg['Type'] == 'Recording' \
            or msg['Type'] == 'Video' \
            or msg['Type'] == 'Attachment':
        try:
            user_nickname = msg['ActualNickName'][:2]  # 如果是群消息会从这里获取昵称
        except:
            user_nickname = msg_from_user_name  # 如果是单人消息从这里获取昵称
        timnum = time.strftime("%Y%m%d%H%M%S", time.localtime())
        msg_content = user_nickname + '_' + timnum + user_nickname + msg['FileName']
        # print('图片 content', msg_content)
        # msg['Text'](rec_tmp_dir + msg['FileName'])
        msg['Text'](rec_tmp_dir + msg_content)  # 保存文件到相应文件夹
    elif msg['Type'] == 'Sharing':
        msg_content = msg['Text']
        msg_share_url = msg['Url']

    rec_msg_dict.update({
        'msg_id': msg_id,
        'msg_from_user': msg_from_user,  # 发消息的用户 id
        'msg_time_rec': msg_time_rec,
        'msg_type': msg_type,
        'msg_content': msg_content,
        'msg_from_user_name': msg_from_user_name,   #发消息用户 id
    })
    face_bug = msg_content  #针对表情包内容
    msg_information.update(
        {
            msg_id: {
                "msg_from": msg_from_user_name, "msg_time": msg_time_rec, "msg_time_rec": msg_time_rec,
                "msg_type": msg['Type'],
                "msg_content": msg_content, "msg_share_url": msg_share_url
            }
        })

    return rec_msg_dict

#处理群消息
def deal_group_msg(msg):
    global face_bug
    msg_id = msg['MsgId']   #消息 id
    msg_from_user = msg['ActualUserName']     #来源用户 id  FromUserName的id是登录用户的id

    if msg_from_user == loadUser['UserName']:   #是登录用户自己发的消息
        msg_from_user_name = loadUser['NickName']
        msg_group = msg['ToUserName']  # 自己发的消息群聊名称
    else:
        try:
            msg_from_user_name = msg['User']['NickName'] if u'NickName' in msg['User'] else msg['User'][
                'UserName']  # 来源用户昵称
        except:
            msg_from_user_name = msg['ActualNickName']  # 获取来源用户昵称

        try:
            msg_group = msg['User']['UserName'] if u'UserName' in msg['User'] else msg['User'][
                'ToUserName']  # 接收方 ID（群聊id）
        except:
            msg_group = msg['FromUserName']  # 群聊 id

    msg_group_name = itchat.search_chatrooms(userName=msg_group)['NickName']  # 群聊名称

    msg_content = ''
    msg_time_rec = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    msg_type = msg['Type']  #消息类型

    msg_share_url = None

    if msg['Type'] == 'Text':
        msg_content = msg['Content']
    elif msg['Type'] == 'Picture' \
            or msg['Type'] == 'Recording' \
            or msg['Type'] == 'Video' \
            or msg['Type'] == 'Attachment':
        try:
            user_nickname = msg['ActualNickName'][:2]  # 如果是群消息会从这里获取昵称
        except:
            user_nickname = msg_from_user_name  # 如果是单人消息从这里获取昵称
        timnum = time.strftime("%Y%m%d%H%M%S", time.localtime())
        msg_content = user_nickname + '_' + timnum + user_nickname + msg['FileName']
        # print('图片 content', msg_content)
        # msg['Text'](rec_tmp_dir + msg['FileName'])
        msg['Text'](rec_tmp_dir + msg_content)  # 保存文件到相应文件夹
    elif msg['Type'] == 'Sharing':
        msg_content = msg['Text']
        msg_share_url = msg['Url']

    rec_group_dict.update({
        'msg_id': msg_id,
        'msg_from_user': msg_from_user,  # 发消息的用户 id
        'msg_time_rec': msg_time_rec,
        'msg_type': msg_type,
        'msg_content': msg_content,
        'msg_from_user_name': msg_from_user_name,   #发消息用户 id
        'msg_group': msg_group,  # 群聊 id
        'msg_group_name': msg_group_name,  # 群聊名称
    })
    face_bug = msg_content  #针对表情包内容
    msg_information.update(
        {
            msg_id: {
                "msg_from": msg_from_user_name, "msg_time": msg_time_rec, "msg_time_rec": msg_time_rec,
                "msg_type": msg['Type'],
                "msg_content": msg_content, "msg_share_url": msg_share_url
            }
        })

    return rec_group_dict

#好友消息
@itchat.msg_register([TEXT, PICTURE, RECORDING,SHARING, ATTACHMENT, VIDEO], isFriendChat=True , isGroupChat=False)
def send_msg_test(msg):
    msg_dict = deal_user_msg(msg)
    if msg_dict['msg_content'] == '测试':
        itchat.send_msg('收到测试数据', toUserName=msg_dict['msg_from_user'])

    elif msg_dict['msg_content'] == '@@打卡统计':
        res = getresult()
        group_ids = get_real_chat_room(groupnames)
        for group_id in group_ids:
            itchat.send_msg(res, toUserName=group_id)

    elif msg_dict['msg_content'] == '群聊测试':
        chat_room = itchat.search_chatrooms(name='测试群聊')
        print(chat_room)
        itchat.send_msg('群聊回复测试消息', toUserName=chat_room)


    else:
        r = wxrobot(msg_dict['msg_id'],msg_dict['msg_type'], msg_dict['msg_time_rec'], msg_dict['msg_content'], msg_dict['msg_from_user'], msg['ToUserName'], msg_dict['msg_from_user_name'],
                    itchat.search_friends(userName=msg['ToUserName'])['NickName'], 0, 0, '', '')
        r.insert_db()     #好友消息直接插入数据库
        print('插入数据库成功')


#群聊
#通过群昵称获取真实chatName
def get_real_chat_room(groupnames):
    res = []
    for name in groupnames:
        chat_rooms = itchat.search_chatrooms(name=name)
        # print('chat_rooms:', chat_rooms)
        if (len(chat_rooms) > 0):
            res.append(chat_rooms[0]['UserName'])
    # print('res',res)
    return res
#群消息
@itchat.msg_register([TEXT, PICTURE, RECORDING, ATTACHMENT, VIDEO], isGroupChat=True)
def reply_msg(msg):
    deal_rep = deal_group_msg(msg)

    deal_rep['msg_user_nickname'] = msg['ActualNickName']  # 用户备注昵称
    group_id = get_real_chat_room(groupnames)  # [...,...]

    if deal_rep['msg_group'] in group_id:

        # itchat.search_friends()['NickName']   是扫码登录用户
        # msg['ActualNickName']     发送消息用户

        r = wxrobot(deal_rep['msg_id'],deal_rep['msg_type'], deal_rep['msg_time_rec'], deal_rep['msg_content'], deal_rep['msg_from_user'], itchat.search_friends()['UserName'],
                    msg['ActualNickName'], itchat.search_friends()['NickName'], msg['isAt'], 1, deal_rep['msg_group'],
                    deal_rep['msg_group_name'])
        r.insert_db()  # 监控的群内，存储所有群消息，包括文件

        if deal_rep['msg_type'] == 'Text':
            characterlist_head = str(deal_rep['msg_content'])[:2]
            if characterlist_head == '打卡':
                stat = Statistical(deal_rep)  # 开始执行打卡信息保存与统计，只保存文本信息
                res = stat.saveuseinfo()
                if res == True:
                    itchat.send_msg('加油，打卡已记录![呲牙]',
                                    toUserName=deal_rep['msg_group'])
                else:
                    time.sleep(1)
                    itchat.send_msg('今日已经打过卡了[抠鼻]', toUserName=deal_rep['msg_group'])
            else:
                print('聊天消息')
    else:
        print('其他群聊消息，不存数据库')



#=======================>微信消息防撤回==============
@itchat.msg_register(NOTE, isFriendChat=True, isGroupChat=True, isMpChat=True)
def recall_msg(msg):
    if '撤回了一条消息' in msg['Content']:
        old_msg_id = re.search("\<msgid\>(.*?)\<\/msgid\>", msg['Content']).group(1)
        # 得到消息
        print('old_msg_id', old_msg_id)
        old_msg = msg_information.get(old_msg_id)
        print(old_msg)

        # 如果发送的是表情
        if len(old_msg_id) < 11:
            itchat.send_file(face_bug, toUserName='filehelper')
        # 发送撤回的提示给文件助手
        else:
            msg_body = "【" \
                       + old_msg.get('msg_from') + "撤回了】\n" \
                       + old_msg.get("msg_type") + "消息:" + "\n" \
                       + old_msg.get("msg_time_rec") + "\n" \
                       + r"" + old_msg.get("msg_content")

        # 如果分享的文件被撤回了，那么就将分享的url加在msg_body中发送给文件助手
        if old_msg['msg_type'] == "Sharing":
            msg_body += "\n就是这个链接>" + old_msg.get('msg_share_url')

        # 将撤回消息发送到文件助手
        itchat.send_msg(msg_body, toUserName="filehelper")

        # 有文件的话也要将文件发送回去
        if old_msg["msg_type"] == "Picture" \
                or old_msg["msg_type"] == "Recording" \
                or old_msg["msg_type"] == "Video" \
                or old_msg["msg_type"] == "Attachment":
            # old_msg['msg_content'] = old_msg['msg_content'].split('@')[-1]
            print('文件名',old_msg['msg_content'])
            file = "@fil@%s" % (rec_tmp_dir + old_msg['msg_content'])
            itchat.send(msg=file, toUserName='filehelper')
            # os.remove(old_msg['msg_content']) #不需要删掉文件吧

        # 删除字典旧信息
        msg_information.pop(old_msg_id)

#登录
if __name__ == '__main__':
    itchat.auto_login(enableCmdQR=2, hotReload=True, loginCallback=after_login, exitCallback=after_logout)
    # 使机器人后台运行，并进入交互模式
    itchat.run()
