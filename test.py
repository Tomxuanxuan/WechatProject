# {'MsgId': '981869209476819536',
#  'FromUserName': '@84882c049bd5ffba36052af2d274661188543659478ad8941406555e179402ed',
#  'ToUserName': '@f02631c2a5675dc3e12e356ea75917faba2163072e4b8c24e9e6cf18235d7e65',
#  'MsgType': 1, 'Content': '好友消息', 'Status': 3, 'ImgStatus': 1, 'CreateTime': 1561108120, 'VoiceLength': 0,
#  'PlayLength': 0, 'FileName': '', 'FileSize': '', 'MediaId': '', 'Url': '', 'AppMsgType': 0, 'StatusNotifyCode': 0, 'StatusNotifyUserName': '',
#
#  'RecommendInfo':
#      {'UserName': '', 'NickName': '', 'QQNum': 0, 'Province': '', 'City': '', 'Content': '', 'Signature': '', 'Alias': '', 'Scene': 0, 'VerifyFlag': 0, 'AttrStatus': 0, 'Sex': 0, 'Ticket': '', 'OpCode': 0},
#
#  'ForwardFlag': 0,
#  'AppInfo': {'AppID': '', 'Type': 0},
#
#  'HasProductId': 0, 'Ticket': '', 'ImgHeight': 0, 'ImgWidth': 0, 'SubMsgType': 0, 'NewMsgId': 981869209476819536, 'OriContent': '', 'EncryFileName': '',
#
#  'User':
#     <User: {'MemberList': <ContactList: []>, 'Uin': 0, 'UserName': '@84882c049bd5ffba36052af2d274661188543659478ad8941406555e179402ed', 'NickName': '浮云', 'HeadImgUrl': '/cgi-bin/mmwebwx-bin/webwxgeticon?seq=691054547&username=@84882c049bd5ffba36052af2d274661188543659478ad8941406555e179402ed&skey=@crypt_ce55c70d_4436b557f729a10e149345bda221bc9a', 'ContactFlag': 1, 'MemberCount': 0, 'RemarkName': '', 'HideInputBarFlag': 0, 'Sex': 0, 'Signature': '', 'VerifyFlag': 0, 'OwnerUin': 0, 'PYInitial': 'FY', 'PYQuanPin': 'fuyun', 'RemarkPYInitial': '', 'RemarkPYQuanPin': '', 'StarFriend': 0, 'AppAccountFlag': 0, 'Statues': 0, 'AttrStatus': 233767, 'Province': '', 'City': '', 'Alias': '', 'SnsFlag': 1, 'UniFriend': 0, 'DisplayName': '', 'ChatRoomId': 0, 'KeyWord': '', 'EncryChatRoomId': '', 'IsOwner': 0}>,
#
# 'Type': 'Text',
# 'Text': '好友消息'}

def deal_user_msg(msg):
    global face_bug
    msg_id = msg['MsgId']   #消息 id
    msg_from_user = msg['FromUserName']     #来源用户 id
    print(msg_from_user,loadUser['UserName'])

    if msg_from_user == loadUser['UserName']:   #是登录用户自己发的消息
        print('走这里')
        msg_from_user_name = loadUser['NickName']
        msg_group = msg['ToUserName']  # 自己发的消息群聊名称
        msg_group_name = itchat.search_friends(userName=msg_group)['NickName']  #群聊名称
        print(msg_group_name)
    else:
        try:
            msg_from_user_name = msg['User']['NickName'] if u'NickName' in msg['User'] else msg['User']['UserName'] #来源用户昵称
        except:
            msg_from_user_name = itchat.search_friends(userName=msg['FromUserName'])['NickName']

        try:
            msg_group = msg['User']['UserName'] if u'UserName' in msg['User'] else msg['User'][
                'ToUserName']  # 接收方 ID（群聊id）
        except:
            msg_group = msg_from_user
        msg_group_name = msg_from_user_name  # 群聊名称

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
        print(msg_share_url)

    rec_msg_dict.update({
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

    return rec_msg_dict
