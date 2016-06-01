# --*-- coding: utf-8 --*--
# author: zwei
# email: suifeng20@hotmail.com

'''
Parse html file
'''
import re
import six
import datetime
from bs4 import BeautifulSoup

from weibo import exception


class HBeautifulSoup(BeautifulSoup):
    pass


class Soup(object):
    def __init__(self, *args, **kwargs):
        self.parser_type = "html.parser"
        self.soup = None

    def __call__(self, wb, **kwargs):
        if not wb:
            raise

        self.soup = HBeautifulSoup(wb, self.parser_type)

    def __getattr__(self, key):
        if self.soup:
            return getattr(self.soup, key)
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def get(self, key, default=None):
        return getattr(self, key, default)

class JDetail(object):
    '''
    pasre WB_detail info
    '''
    def __init__(self, *args, **kwargs):
        self.content = kwargs.get('content', None)
        self.jx = Soup()

    def __call__(self, WB, **kwargs):
        self.wb = self._get_wb_html(WB)
        self.jx(self.wb)

    def _get_wb_html(self, WB, content=None):
        if content is None:
            content = self.content

        # 确保完整的html 信息
        WB = WB[25:-20]
        # 去掉 "\\n, \\r, \\t, \\/, \\"
        WB = WB.replace('\\n','').\
                replace('\\t','').\
                replace('\\r','').\
                replace('\\/','/').\
                replace('\\','').strip()
        return WB

    # 获取 文本信息中的 表情 图片
    def _get_wb_img_link(self):
        pass

    # 获取 文本信息中的 视频 链接地址
    def _get_wb_a_link(self):
        pass

    def _get_zf_wb(self):
        text_div = self._get_wb_text(zf=False)

    def _get_wb_text(self, zf=False):
        if not zf:
            div_attrs = {'node-type': 'feed_list_content'}
        else:
            div_attrs = {'node-type': 'feed_list_reason'}
        text_divs = self.jx.findAll(name='div', attrs=div_attrs)
        if len(text_divs) != 1:
            raise exception.NotFounddivtexttag()
        text_div = text_divs[0]
        return text_div

    def _get_wb_children(self, div):
        pass

    def _resolve_text(self, text):
        if not isinstance(text, six.text_type):
            text = unicode(text, 'utf-8')
        return text.strip()

    def _get_wb_no_children(self, div):
        text = div.text
        text = self._resolve_text(text)
        print(text)
        return text

    def get_wb_text(self):
        import pdb;pdb.set_trace()
        text_div = self._get_wb_text(zf=False)
        if len(list(text_div.children)) > 1:
            self._get_wb_children(text_div)
        else:
            self._get_wb_no_children(text_div)


    def _get_wb_img(self):
        div_attrs = {'node-type': 'feed_list_media_prev'}
        img_divs = self.jx.findAll(name='div', attrs=div_attrs)
        if len(img_divs) != 1:
            raise exception.NotFounddivtexttag()
        img_div = img_divs[0]

    def get_wb_img(self):
        import pdb;pdb.set_trace()

class Jhtml(object):
    '''
    This class pasre some html file
    use re module
    '''

    def __init__(self, *args, **kwargs):
        self.weibodata = []

    def __call__(self, content):
        self.jiexi2(content)
        self.jdetail = JDetail()

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
        WB_detail = re.findall(r"WB\_detail(.+?)WB\_detail", content)
        return WB_detail

    def wb_text(self, WB):
        # 正文
        self.jdetail(WB)
        self.jdetail.get_wb_text()
        #WB_text = ''.join(re.findall(r"WB\_text[^>]*>(.*?)<\\/div", WB)).replace('\\n', '').replace('\\"', '"').replace('\\/', '/').strip()
        #return WB_text

    def wb_img(self, WB):
        # 图片
        #reg = r'src="(.*?\.jpg)"'
        #WB_img = ''.join(re.findall(r'src=.*.sinaimg.cn.*.jpg', WB))
        #return WB_img
        self.jdetail(WB)
        self.jdetail.get_wb_text()

    def wb_videos(self, WB):
        # 视频
        pass

    def wb_url(self, WB):
        # 图片和视频的url 地址
        pass

    def wb_favorite(self, WB):
        # 收藏
        try:
            WB_favorite = re.findall(r'ficon\_favorite[^>]*>(.)<\\/em><em>(\w+)<\\/em>', WB)[-1][-1] #checked
        except IndexError:
            WB_favorite = '收藏'
        return WB_favorite

    def wb_forward(self, WB):
        # 转发
        try:
            WB_forward = re.findall(r'<em>(\d+)<\\/em>', WB)[0] #checked
        except IndexError:
            WB_forward = 0
        return WB_forward

    def wb_repeat(self, WB):
        # 评论
        # WB_repeat = re.findall(r'ficon\_repeat[^>]*>(&#xe\d+;)<\\/em><em>(\d+)<\\/em>', WB)[-1][-1] #checked
        try:
            WB_repeat = re.findall(r'<em>(\d+)<\\/em>', WB)[1] #checked
        except IndexError:
            WB_repeat = 0
        return WB_repeat

    def wb_praised(self, WB):
        # 点赞
        try:
            WB_praised = re.findall(r'<em>(\d+)<\\/em>', WB)[2] #checked
        except IndexError:
            WB_praised = 0
        return WB_praised


    def wb_time(self, WB):
        try:
            WB_timestamp = re.findall(r'date=\\"([^"]*)\\"', WB)[-1]  # checked
        except IndexError:
            WB_timestamp = 0
        dateArray = datetime.datetime.utcfromtimestamp(int(WB_timestamp) / 1000)
        otherStyleTime = dateArray.strftime("%Y-%m-%d %H:%M:%S")
        return int(WB_timestamp) / 1000

    def wb_like(self, WB):
        WB_like = ''.join(re.findall(r'WB\_text[^>]*>.*praised.*?\(([0-9]*)', WB))  # checked
        return WB_like


    def wb_mid(self, WB):
        # 获取微博id
        try:
            WB_mid = re.findall(r'mid=.*?(\d*)', WB)[-1]  # checked
        except IndexError:
            raise exception.NotFoundMid(mid=WB_mid)
        return WB_mid


    def wb_name(self, WB):
        # 微博作者的用户信息字段
        WB_name = ''.join(re.findall(r'nick-name=\\"([^"]*)\\"', WB))
        return WB_name


    def wb_uid(self, WB):
        # 微博的作者id
        WB_uid = ''.join(re.findall(r'fuid=([^"]*)\\"', WB))  # checked
        return WB_uid

    def wb_all_jiexi2(self, wb_detail):
        weibodata = {}
        for wb in wb_detail:
            weibodata['uid'] = self.wb_uid(wb)
            weibodata['mid'] = self.wb_mid(wb)
            weibodata['name'] = self.wb_name(wb)
            weibodata['time'] = self.wb_time(wb)
            weibodata['text'] = self.wb_text(wb)
            weibodata['img'] = self.wb_img(wb)
            weibodata['favorite'] = self.wb_favorite(wb)
            weibodata['forward'] = self.wb_forward(wb)
            weibodata['repeat'] = self.wb_repeat(wb)
            weibodata['praised'] = self.wb_praised(wb)
            self.weibodata.append(weibodata)

        return self.weibodata


    def jiexi2(self, content=None):
        if content is None:
            raise exception.NotFoundContent()

        if six.PY3:
            content = content.decode('utf-8')

        content = self.tmp_file(content)
        wb_detail = self.wb_detail(content)
        return self.wb_all_jiexi2(wb_detail)

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
            # WB_source = ''.join(re.findall(r'WB\_text[^>]*>.*nofollow\\">(.*?)<', WB))  # checked

            # 图片收集
            #import pdb;pdb.set_trace()
            #reg = r'src="(.*?\.jpg)"'
            #WB_img = ''.join(re.findall(r'src=.*.sinaimg.cn.*.jpg', WB))

            # 收藏
            #WB_favorite = re.findall(r'ficon\_favorite[^>]*>(.)<\\/em><em>(\w+)<\\/em>', WB)[-1][-1] #checked
            #WB_favorite = re.findall(r'收藏|已收藏', WB)  # checked

            # 转发
            WB_forward = re.findall(r'<em>(\d+)<\\/em>', WB)[0] #checked

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
