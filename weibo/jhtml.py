# --*-- coding: utf-8 --*--
# author: zwei
# email: suifeng20@hotmail.com

'''
Parse html file
'''

class Html(object):
    '''
    This class pasre some html file
    use re module
    '''
    def __init__(self, *args, **kwargs):
        pass

    def tmp_file(self, content):
        tmp = re.findall(r'pl\.content\.homeFeed\.index.*html\":\"(.*)\"}\)', content)
        for tmp_r in tmp:
            content = content.replace(tmp_r, 's')

        max = 0
        for i in tmp:
            if max < len(i):
                max = len(i)
                content = i

        content = content.replace('WB_detail', 'WB_detailWB_detail')
        return content

    def wb_detail(self, content):
        # get all things from WB_detail
        WB_single = re.findall(r"WB\_detail(.+?)WB\_detail", content)
        return WB_single

    def wb_text(self, WB):
        # 正文
        WB_text = ''.join(re.findall(r"WB\_text[^>]*>(.*?)<\\/div", WB)).replace('\\n', '').replace('\\"', '"').replace('\\/', '/').strip()
        #.lstrip('\\n').strip()

    def wb_img(self, WB):
        # 图片
        reg = r'src="(.*?\.jpg)"'
        WB_img = ''.join(re.findall(r'src=.*.sinaimg.cn.*.jpg', WB))

    def wb_videos(self, WB):
        # 视频
        pass

    def wb_url(self, WB):
        # 图片和视频的url 地址
        pass

    def wb_favorite(self, WB):
        WB_favorite = re.findall(r'ficon\_favorite[^>]*>(.)<\\/em><em>(\w+)<\\/em>', WB)[-1][-1] #checked

    def wb_forward(self, WB):
        # 转发
        WB_forward = re.findall(r'<em>(\d+)<\\/em>', WB)[0] #checked

    def wb_repeat(self, WB):
        # 评论
        WB_repeat = re.findall(r'<em>(\d+)<\\/em>', WB)[1] #checked
        WB_repeat = re.findall(r'ficon\_repeat[^>]*>(&#xe\d+;)<\\/em><em>(\d+)<\\/em>', WB)[-1][-1] #checked

    def wb_praised(self, WB):
        # 点赞
        WB_praised = re.findall(r'<em>(\d+)<\\/em>', WB)[2] #checked

    def jiexi(self, content=None):
        if six.PY3:
            content = content.decode('utf-8')
            tmp = re.findall(r'pl\.content\.homeFeed\.index.*html\":\"(.*)\"}\)', content)
            # for tmp_r in tmp:
                # content = content.replace(tmp_r, 's')
            max = 0
            for i in tmp:
                if max < len(i):
                    max = len(i)
                    content = i
                    content = content.replace('WB_detail', 'WB_detailWB_detail')
                    # get all things
                    WB_single = re.findall(r"WB\_detail(.+?)WB\_detail", content)
                    # for i in range(0,len(WB_single)):
                        # {'text': 微博信息内容, 'count': 转发数, 'wid': 微博ID, 'name': 微博作者的用户信息字段, 'uid': 用户UID,
                        #  'nick': 用户昵称, 'self': u['self'], 'timestamp': 微博创建时间, 'source': 微博来源,
                        #  'location': 用户所在地, 'country_code': u['country_code'],
                        #  'province_code': 用户所在省级ID, 'city_code': 用户所在城市ID, 'geo': 地理信息字段,
                        #  'emotionurl': u['emotionurl'], 'emotiontype': u['emotiontype']
                        # })
                        # {'text': u['text'], 'count': u['reposts_count'], 'wid': u['id'], 'name': u['user']['name'],
                        #  'uid': u['user']['id'],
                        #  'nick': u['user']['screen_name'], 'self': 'null', 'timestamp': u['created_at'], 'source': u['source'],
                        #  'location': u['user']['location'], 'country_code': '',
                        #  'province_code': u['user']['province'], 'city_code': u['user']['city'], 'geo': u['geo'],
                        #  # 'emotionurl': u['emotionurl'], 'emotiontype': u['emotiontype']
                        #  'link': u['user']['id']
                        # })

        user = []
    for WB in WB_single:
        # 正文
        #import pdb;pdb.set_trace()
        WB_text = ''.join(re.findall(r"WB\_text[^>]*>(.*?)<\\/div", WB)).replace('\\n', '').replace('\\"', '"').replace('\\/', '/').strip()  #.lstrip('\\n').strip()

        # if WB_text inclued WB_media_expand is miniPage !!!!!!
        #WB_source = ''.join(re.findall(r'WB\_text[^>]*>.*nofollow\\">(.*?)<', WB))  # checked

        # 图片收集
        #import pdb;pdb.set_trace()
        #reg = r'src="(.*?\.jpg)"'
        #WB_img = ''.join(re.findall(r'src=.*.sinaimg.cn.*.jpg', WB))

        # 收藏
        #WB_favorite = re.findall(r'ficon\_favorite[^>]*>(.)<\\/em><em>(\w+)<\\/em>', WB)[-1][-1] #checked
        #WB_favorite = re.findall(r'收藏|已收藏', WB)  # checked

        # 转发
        #WB_forward = re.findall(r'<em>(\d+)<\\/em>', WB)[0] #checked

        # 评论
        #WB_repeat = re.findall(r'<em>(\d+)<\\/em>', WB)[1] #checked
        #WB_repeat = re.findall(r'ficon\_repeat[^>]*>(&#xe\d+;)<\\/em><em>(\d+)<\\/em>', WB)[-1][-1] #checked

        # 点赞
        #WB_praised = re.findall(r'<em>(\d+)<\\/em>', WB)[2] #checked

        WB_like = ''.join(re.findall(r'WB\_text[^>]*>.*praised.*?\(([0-9]*)', WB))  # checked
        WB_mid = re.findall(r'mid=.*?(\d*)', WB)[-1]  # checked
        WB_name = ''.join(re.findall(r'nick-name=\\"([^"]*)\\"', WB))
        WB_uid = ''.join(re.findall(r'fuid=([^"]*)\\"', WB))  # checked
        WB_timestamp = re.findall(r'date=\\"([^"]*)\\"', WB)[-1]  # checked

        dateArray = datetime.datetime.utcfromtimestamp(int(WB_timestamp) / 1000)
        otherStyleTime = dateArray.strftime("%Y-%m-%d %H:%M:%S")

        user.append({
            'text': WB_text,
            #'source': WB_source,
            #'收藏': WB_favorite,
            #'转发': WB_forward,
            #'评论': WB_repeat,
            #'点赞': WB_praised,
            'time': otherStyleTime,
            'mid': WB_mid,
            'name': WB_name,
            'uid': WB_uid,
            'nick': WB_name,
            'self': 'dontknow', 'location': 'null', 'country_code': '', 'province_code': 'null',
            'city_code': 'null',
            'geo': 'null',
            'link': WB_uid,
            'like': WB_like,
        })

    return user, len(user)

