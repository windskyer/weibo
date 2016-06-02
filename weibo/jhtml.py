# --*-- coding: utf-8 --*--
# author: zwei
# email: suifeng20@hotmail.com

'''
Parse html file
'''
import re
import six
import json
import datetime
from bs4.element import Tag
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

class ZDetail(object):
    def __init__(self, z_jx, jdetail):
        self.z_jx = z_jx
        self.jx = jdetail

    def get_wb_text(self, zf=True):
        return self.jx.get_wb_text(self.z_jx, zf)

    def get_wb_img(self, zf=True):
        return self.jx.get_wb_img(self.z_jx, zf)

    def get_wb_videos(self, zf=True):
        return self.jx.get_wb_videos(self.z_jx, zf)


class JDetail(object):
    '''
    pasre WB_detail info
    '''
    def __init__(self, *args, **kwargs):
        self.content = kwargs.get('content', None)
        self.jx = Soup()
        self.z_jx = None
        self.wb_2frp = None

    def __call__(self, WB, **kwargs):
        wb = self._get_wb_html(WB)
        self.jx(wb)

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

    # 是否是转发微博
    @property
    def is_zf_wb(self):
        div_attrs = {'class': 'WB_feed_expand'}
        z_jx = self.jx.findChild(name='div', attrs=div_attrs)
        if z_jx is None:
            return False
        self.get_zf_wb(z_jx)
        return True

    def get_zf_wb(self, z_jx=None):
        if not isinstance(z_jx, Tag):
            raise exception.NotFoudZfweibo()

        div_attrs = {'node-type': 'feed_list_forwardContent'}
        z_jx = z_jx.findChild(name='div', attrs=div_attrs)
        self.z_jx = ZDetail(z_jx, self)


    # 获取 正常的 text 文本信息
    def _resolve_text(self, text):
        if not isinstance(text, six.text_type):
            text = unicode(text, 'utf-8')
        return text.strip()

    # 获取下一个 第一个 tag
    def _get_children_tag(self, jx, name=None, attrs={}, **kwargs):
        children = jx.findChild(name, attrs, **kwargs)
        if not children:
            attrs = json.dumps(attrs)
            raise exception.NotFoundChildrenTag(name, attrs)
        return children


    # 获取 文本信息
    # 获取 文本信息中的 表情 图片
    def _get_wb_img_link(self, jx, *args, **kwargs):
        pass

    # 获取 文本信息中的 视频 链接地址
    def _get_wb_a_link(self, jx, *args, **kwargs):
        pass

    # 获取文本信息中的 子信息
    def _get_wb_children(self, div):
        pass

    # 获取文本信息中的 没有 子信息
    def _get_wb_no_children(self, div):
        text = div.text
        text = self._resolve_text(text)
        return text

    def _get_wb_text(self, jx, zf=False):
        if not zf:
            div_attrs = {'node-type': 'feed_list_content'}
        else:
            div_attrs = {'node-type': 'feed_list_reason'}
        text_div = self._get_children_tag(jx=jx, name='div', attrs=div_attrs)
        return text_div

    # 获取 text 信息
    def get_wb_text(self, jx=None, zf=False):
        if not jx:
            jx = self.jx
        texts = {'is_zf': zf}
        text_div = self._get_wb_text(jx, zf)
        if len(list(text_div.children)) > 1:
            text = self._get_wb_children(text_div)
        else:
            text = self._get_wb_no_children(text_div)
        texts.setdefault('text', text)
        return texts

    # start 获取img 或者 videos 的 url 地址
    def _get_wb_img_ul(self, i_v_div):
        img_urls = []
        uls = i_v_div.findAll('ul')
        for ul in uls:
            urls = self._get_wb_img_li(ul)
            img_urls.extend(urls)
        return img_urls

    def _get_wb_img_li(self, i_v_div_ul):
        img_urls = []
        lis = i_v_div_ul.findAll('li')
        for li in lis:
            url = self._get_wb_li_img(li)
            if url:
                img_urls.append(url)
        return img_urls

    def _get_wb_li_img(self, li):
        img = li.img
        attrs = img.attrs
        return attrs.get('src', None)

    # 查询下一个 子 的 div
    def _get_wb_img_or_videos(self, jx=None):
        if not jx:
            jx = self.jx
        div_attrs = {'class': 'WB_media_wrap clearfix',
                     'node-type': 'feed_list_media_prev'}
        # find first img div
        try:
            img_videos_div = self._get_children_tag(jx=jx,
                                                    name='div',
                                                    attrs=div_attrs)
        except excetion.NotFoundChildrenTag:
            return None
        return img_videos_div

    # 获取 img 和videos 的url 地址
    def get_wb_img_or_videos(self, jx, zf=False):
        if not jx:
            jx = self.jx
        img_urls = {'is_zf': zf}
        i_v_div = self._get_wb_img_or_videos(jx)
        if not i_v_div:
            urls = None
        else:
            urls = self._get_wb_img_ul(i_v_div)
        img_urls.setdefault('urls', urls)
        return img_urls

    # 获取所有图片的信息
    def get_wb_img(self, jx=None, zf=False):
        return self.get_wb_img_or_videos(jx, zf)

    # 获取所有视频的信息
    def get_wb_videos(self, jx=None, zf=False):
        pass

    # end 获取 img or videos 的 url


    # 获取 收藏, 转发, 评论, 点赞 数据
    def _get_wb_2frp_em(self, a, zf=False):
        ems = a.findAll('em')
        if not len(ems):
            return "收藏"
        em = self._resolve_text(ems[-1].text)
        return em

    def _get_wb_2frp_a(self, li, zf=False):
        a = li.find('a')
        return self._get_wb_2frp_em(a, zf)

    def _get_wb_2frp_li(self, ul, zf=False):
        lis = ul.findAll('li')
        li_texts = []
        for li in lis:
            li_text = self._get_wb_2frp_a(li, zf)
            li_texts.append(li_text)
        return li_texts

    def _get_wb_2frp_ul(self, div_2frp, zf=False):
        wb_2frp = []
        uls = div_2frp.findAll('ul')
        for ul in uls:
            ems = self._get_wb_2frp_li(ul)
            wb_2frp.extend(ems)
        return wb_2frp

    def _get_wb_2frp(self, jx, zf=False):
        div_attrs = {'class': 'WB_feed_handle',
                     'node-type': 'feed_list_options'}
        if not jx:
            jx = self.jx

        zfrp_div = self._get_children_tag(jx=jx,
                                          name='div',
                                          attrs=div_attrs)

        return zfrp_div

    def get_wb_2frp(self, jx=None, zf=False):
        if not jx:
            jx = self.jx
        wb_2frp = self._get_wb_2frp(jx, zf)
        self.wb_2frp = self._get_wb_2frp_ul(wb_2frp, zf)

    def get_wb_favorite(self, jx=None, zf=False):
        # 收藏
        import pdb;pdb.set_trace()
        return self.wb_2frp[0]

    def get_wb_forward(self, jx=None, zf=False):
        # 转发
        try:
            fd = eval(self.wb_2frp[1])
        except:
            return 0
        else:
            return fd

    def get_wb_repeat(self, jx=None, zf=False):
        # 评论
        try:
            rt = eval(self.wb_2frp[2])
        except:
            return 0
        else:
            return rt

    def get_wb_praised(self, jx=None, zf=False):
        # 点赞
        try:
            pd = eval(self.wb_2frp[3])
        except:
            return 0
        else:
            return pd

class Jhtml(object):
    '''
    This class pasre some html file
    use re module
    '''

    def __init__(self, *args, **kwargs):
        self.weibodata = []

    def __call__(self, content):
        self.jdetail = JDetail()
        self.jiexi2(content)

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

    def is_zf_wb(self, WB=None):
        if WB:
            self.jdetail(WB)
        return self.jdetail.is_zf_wb

    def wb(self, WB):
        self.jdetail(WB)
        self.jdetail.get_wb_2frp()

    def wb_text(self, WB=None, zf=False):
        # 正文
        if zf:
            text = self.jdetail.z_jx.get_wb_text()
        else:
            text = self.jdetail.get_wb_text()
        #WB_text = ''.join(re.findall(r"WB\_text[^>]*>(.*?)<\\/div", WB)).replace('\\n', '').replace('\\"', '"').replace('\\/', '/').strip()
        return text

    def wb_img(self, WB=None, zf=False):
        # 图片
        #reg = r'src="(.*?\.jpg)"'
        #WB_img = ''.join(re.findall(r'src=.*.sinaimg.cn.*.jpg', WB))
        if zf:
            img = self.jdetail.z_jx.get_wb_img()
        else:
            img = self.jdetail.get_wb_img()
        return img

    def wb_videos(self, WB, zf=False):
        # 视频
        pass

    def wb_favorite(self, WB, zf=False):
        return self.jdetail.get_wb_favorite()
        # 收藏
        #try:
        #    WB_favorite = re.findall(r'ficon\_favorite[^>]*>(.)<\\/em><em>(\w+)<\\/em>', WB)[-1][-1] #checked
        #except IndexError:
        #    WB_favorite = '收藏'
        #return WB_favorite
        #return favortie

    def wb_forward(self, WB, zf=False):
        return self.jdetail.get_wb_forward()
        # 转发
        #try:
        #    WB_forward = re.findall(r'<em>(\d+)<\\/em>', WB)[0] #checked
        #except IndexError:
        #    WB_forward = 0
        #return WB_forward

    def wb_repeat(self, WB, zf=False):
        # 评论
        # WB_repeat = re.findall(r'ficon\_repeat[^>]*>(&#xe\d+;)<\\/em><em>(\d+)<\\/em>', WB)[-1][-1] #checked
        #try:
        #    WB_repeat = re.findall(r'<em>(\d+)<\\/em>', WB)[1] #checked
        #except IndexError:
        #    WB_repeat = 0
        #return WB_repeat
        pass

    def wb_praised(self, WB, zf=False):
        # 点赞
        #try:
        #    WB_praised = re.findall(r'<em>(\d+)<\\/em>', WB)[2] #checked
        #except IndexError:
        #    WB_praised = 0
        #return WB_praised
        pass


    def wb_time(self, WB, zf=False):
        if zf:
            return
        try:
            WB_timestamp = re.findall(r'date=\\"([^"]*)\\"', WB)[-1]  # checked
        except IndexError:
            WB_timestamp = 0
        dateArray = datetime.datetime.utcfromtimestamp(int(WB_timestamp) / 1000)
        otherStyleTime = dateArray.strftime("%Y-%m-%d %H:%M:%S")
        return int(WB_timestamp) / 1000

    def wb_mid(self, WB, zf=False):
        # 获取微博id
        try:
            WB_mid = re.findall(r'mid=.*?(\d*)', WB)[-1]  # checked
        except IndexError:
            raise exception.NotFoundMid(mid=WB_mid)
        return WB_mid

    def wb_like(self, WB, zf=False):
        WB_like = ''.join(re.findall(r'WB\_text[^>]*>.*praised.*?\(([0-9]*)', WB))  # checked
        return WB_like

    def wb_name(self, WB, zf=False):
        # 微博作者的用户信息字段
        if not zf:
            WB_name = ''.join(re.findall(r'nick-name=\\"([^"]*)\\"', WB))
        else:
            return
        return WB_name


    def wb_uid(self, WB, zf=False):
        # 微博的作者id
        if not zf:
            WB_uid = ''.join(re.findall(r'fuid=([^"]*)\\"', WB))  # checked
        else:
            WB_uid = 0
        return WB_uid

    def get_wb_info(self, wb=None, zf=False):
        wb_info = {}
        wb_info['favorite'] = self.wb_favorite(wb, zf)
        wb_info['forward'] = self.wb_forward(wb, zf)
        wb_info['text'] = self.wb_text(wb, zf)
        wb_info['img'] = self.wb_img(wb, zf)
        #wb_info['uid'] = self.wb_uid(wb, zf)
        #wb_info['mid'] = self.wb_mid(wb, zf)
        #wb_info['name'] = self.wb_name(wb, zf)
        #wb_info['time'] = self.wb_time(wb, zf)
        #wb_info['repeat'] = self.wb_repeat(wb, zf)
        #wb_info['praised'] = self.wb_praised(wb, zf)
        return wb_info

    def wb_all_jiexi2(self, wb_detail):
        weibodata = {}
        for wb in wb_detail:
            import pdb;pdb.set_trace()
            # 初始化wb 信息
            self.wb(wb)
            wb = self.get_wb_info(wb, False)
            weibodata.setdefault('wb', wb)
            if self.is_zf_wb():
                zf_wb = self.get_wb_info(wb, True)
                weibodata.setdefault('zf_wb', zf_wb)
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
