# --*-- coding: utf-8 --*--
# author: zwei
# email: suifeng20@hotmail.com

'''
Parse html file
'''
import re
import six
import urlparse
from bs4.element import Tag
from bs4 import BeautifulSoup

from weibo import exception
from weibo.jiexi import userinfo
from weibo.common.gettextutils import _
from weibo.common import log as logging

LOG = logging.getLogger(__name__)


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
        self._get_wb_mid_date()
        self._get_wb_uid_name()
        return self.jx.get_wb_text(self.z_jx, zf)

    def get_wb_img(self, zf=True):
        return self.jx.get_wb_img(self.z_jx, zf)

    def get_wb_videos(self, zf=True):
        return self.jx.get_wb_videos(self.z_jx, zf)

    def _get_wb_mid_date(self, zf=True):
        self.jx._get_wb_mid_date(self.z_jx, zf)

    def _get_wb_uid_name(self, zf=True):
        self.jx._get_wb_uid_name(self.z_jx, zf)

    def get_wb_mid(self, zf=True):
        return self.jx.get_wb_mid(self.z_jx, zf)

    def get_wb_uid(self, zf=True):
        return self.jx.get_wb_uid(self.z_jx, zf)

    def get_wb_date(self, zf=True):
        return self.jx.get_wb_date(self.z_jx, zf)

    def get_wb_name(self, zf=True):
        return self.jx.get_wb_name(self.z_jx, zf)


class JDetail(object):
    '''
    pasre WB_detail info
    '''
    def __init__(self, *args, **kwargs):
        self.content = kwargs.get('content', None)
        self.jx = Soup()
        self.z_jx = None
        self.is_zf = False
        self.wb_2frp = None
        self.wb_mid_date = {}
        self.wb_uid_name = {}

    def __call__(self, WB, **kwargs):
        wb = self._get_wb_html(WB)
        self.jx(wb)

    def _get_wb_html(self, WB, content=None):
        if content is None:
            content = self.content

        # 去掉 "\\n, \\r, \\t, \\/, \\"
        WB = WB.replace('\\n', '')
        WB = WB.replace('\\t', '')
        WB = WB.replace('\\r', '')
        WB = WB.replace('\\/', '/')
        WB = WB.replace('\\', '')

        # 确保完整的html 信息
        WB = WB[WB.find('>') + 1:WB.rfind('<')]
        return WB.strip()

    # 是否是转发微博
    @property
    def is_zf_wb(self):
        div_attrs = {'class': 'WB_feed_expand'}
        z_jx = self.jx.findChild(name='div', attrs=div_attrs)
        if z_jx and not self.is_zf_wb_and_delete(z_jx):
            self.is_zf = True
            self.get_zf_wb(z_jx)
        else:
            self.is_zf = False

        return self.is_zf

    # 是转发微博 但是 转发被删除
    def is_zf_wb_and_delete(self, z_jx):
        div_attrs = {'class': 'WB_empty'}
        try:
            self._get_children_tag(z_jx, name='div', attrs=div_attrs)
        except exception.NotFoundChildrenTag:
            return False
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
            attrs.setdefault('name', name)
            attrs.setdefault('class', None)
            attrs.setdefault('node-type', None)
            LOG.debug(_("children %(name)s, %(class)s, "
                        "%(node-type)s"), attrs)
            raise exception.NotFoundChildrenTag(attrs)
        return children

    # 获取 微博的uid, name 等
    def _get_wb_uid_name(self, jx=None, zf=False):
        self.wb_uid_name = {}
        if not jx:
            jx = self.jx
        if not zf:
            div_attrs = {'class': 'WB_info'}
            uidname_div = self._get_children_tag(jx,
                                                 name='div',
                                                 attrs=div_attrs)
            a_first = self._get_children_tag(uidname_div,
                                             name='a')
            name = a_first.get_text()

            usercard = a_first.attrs.get('usercard', None)
            usercard = urlparse.parse_qsl(usercard)
            usercard = dict(usercard)
            uid = usercard.get('id', None)

            self.wb_uid_name['name'] = name
            self.wb_uid_name['uid'] = uid
        else:
            div_attrs = {'class': 'WB_info'}
            uidname_div = self._get_children_tag(jx,
                                                 name='div',
                                                 attrs=div_attrs)
            a_first = self._get_children_tag(uidname_div,
                                             name='a')
            usercard = a_first.attrs.get('usercard', None)
            usercard = urlparse.parse_qsl(usercard)
            usercard = dict(usercard)
            uid = usercard.get('id', None)
            self.wb_uid_name['uid'] = uid

            nickname = a_first.attrs.get('nick-name', None)
            self.wb_uid_name['name'] = nickname

            midstr = a_first.attrs.get('suda-uatrack', None)
            midstr = urlparse.parse_qsl(midstr)
            midstr = dict(midstr)
            midstr = midstr.get('value', None)
            midnum = midstr.find(":") + 1
            mid = midstr[midnum:]

            time_at = '0'
            self.wb_mid_date['mid'] = mid
            self.wb_mid_date['time_at'] = time_at

    # 获取 微博的mid, time_at 等
    def _get_wb_mid_date(self, jx=None, zf=False):
        self.wb_mid_date = {}
        if not jx:
            jx = self.jx
        if not zf:
            div_attrs = {'class': 'WB_from S_txt2'}
            middate_div = self._get_children_tag(jx,
                                                 name='div',
                                                 attrs=div_attrs)
            a_first = self._get_children_tag(middate_div,
                                             name='a')
            mid = a_first.attrs.get('name', None)
            time_at = a_first.attrs.get('date', '0')
            self.wb_mid_date['mid'] = mid
            self.wb_mid_date['time_at'] = time_at
        else:
            self._get_wb_uid_name(jx, zf)

    # 获取 mid
    def get_wb_mid(self, jx=None, zf=False):
        return self.wb_mid_date.get('mid', None)

    # 获取 time_at 时间
    def get_wb_date(self, jx=None, zf=False):
        return self.wb_mid_date.get('time_at', None)

    # 获取 uid
    def get_wb_uid(self, jx=None, zf=False):
        return self.wb_uid_name.get('uid', None)

    # 获取 name
    def get_wb_name(self, jx=None, zf=False):
        return self.wb_uid_name.get('name', None)

    # 获取 文本信息
    # 获取 文本信息中的 表情 图片
    def _get_wb_img_link(self, jx=None, *args, **kwargs):
        pass

    # 获取 文本信息中的 视频 链接地址
    def _get_wb_a_link(self, jx=None, *args, **kwargs):
        pass

    # 获取文本信息中的 子信息
    def _get_wb_children(self, div):
        text = div.text
        text = self._resolve_text(text)
        return text

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
        except exception.NotFoundChildrenTag:
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
        if self.is_zf != zf:
            return
        return self.get_wb_img_or_videos(jx, zf)

    # 获取所有视频的信息
    def get_wb_videos(self, jx=None, zf=False):
        if self.is_zf_wb != zf:
            return
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
        self.userinfo = userinfo.Userinfo()
        self.weibodata = []
        self.weibodata_dict = {}
        self.fl_values = None

    def __call__(self, content):
        self.weibodata = []
        self.jdetail = JDetail()
        wbinfo = self.jiexi2(content)
        self.get_userdata_info(wbinfo, content)

    def tmp_file(self, content):
        tmp = re.findall(r'pl\.content\.homeFeed\.'
                         r'index.*html\":\"(.*)\"}\)', content)
        for tmp_r in tmp:
            content = content.replace(tmp_r, 's')

        max = 0
        for i in tmp:
            if max < len(i):
                max = len(i)
                content = i

        content = content.replace('WB_detail', 'WB_detailWB_detail')
        return content

    def get_userdata_info(self, wbinfo, content):
        uid = wbinfo[0].get('uid', None)
        if uid:
            self.fl_values = self.userinfo.jiexi2(uid, content)
            self.weibodata_dict['userdata'] = self.fl_values
        self.weibodata_dict['weibodata'] = self.weibodata
        return self.weibodata_dict

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
        self.get_wb_and_zf_info()

    def wb_text(self, WB=None, zf=False):
        # 正文
        if zf:
            text = self.jdetail.z_jx.get_wb_text()
        else:
            text = self.jdetail.get_wb_text()
        return text

    def wb_img(self, WB=None, zf=False):
        # 图片
        if zf:
            img = self.jdetail.z_jx.get_wb_img()
        else:
            img = self.jdetail.get_wb_img()
        return img

    def wb_videos(self, WB, zf=False):
        # 视频
        pass

    def wb_favorite(self, WB, zf=False):
        # 收藏
        if zf:
            return
        return self.jdetail.get_wb_favorite()

    def wb_forward(self, WB, zf=False):
        # 转发
        if zf:
            return
        return self.jdetail.get_wb_forward()

    def wb_repeat(self, WB, zf=False):
        # 评论
        if zf:
            return
        return self.jdetail.get_wb_repeat()

    def wb_praised(self, WB, zf=False):
        # 点赞
        if zf:
            return
        return self.jdetail.get_wb_praised()

    def get_wb_and_zf_info(self, WB=None, zf=False):
        # 获取weibo 主人的信息
        # 获取 weibo 本身的 信息
        self.jdetail._get_wb_uid_name(zf=zf)
        self.jdetail._get_wb_mid_date(zf=zf)

    def wb_time(self, WB, zf=False):
        # weibo 发布时间
        # WB_timestamp = re.findall(r'date=\\"([^"]*)\\"', WB)[-1]
        # checked
        if not zf:
            WB_timestamp = self.jdetail.get_wb_date()
        else:
            WB_timestamp = self.jdetail.z_jx.get_wb_date()
        return int(WB_timestamp) / 1000

    def wb_mid(self, WB, zf=False):
        # 获取微博id
        # WB_mid = re.findall(r'mid=.*?(\d*)', WB)[-1]
        # checked
        if not zf:
            WB_mid = self.jdetail.get_wb_mid()
        else:
            WB_mid = self.jdetail.z_jx.get_wb_mid()
        return WB_mid

    def wb_like(self, WB, zf=False):
        # weibo like
        WB_like = ''.join(re.findall(r'WB\_text[^>]*>.*'
                                     r'praised.*?\(([0-9]*)', WB))
        # checked
        return WB_like

    def wb_name(self, WB, zf=False):
        # 微博作者的用户信息字段
        if not zf:
            # WB_name = ''.join(re.findall(r'nick-name=\\"([^"]*)\\"', WB))
            WB_name = self.jdetail.get_wb_name()
        else:
            WB_name = self.jdetail.z_jx.get_wb_name()
        return WB_name

    def wb_uid(self, WB, zf=False):
        # 微博的作者id
        if not zf:
            # WB_uid = ''.join(re.findall(r'fuid=([^"]*)\\"', WB))
            WB_uid = self.jdetail.get_wb_uid()
            # checked
        else:
            WB_uid = self.jdetail.z_jx.get_wb_uid()
        return WB_uid

    def get_wb_info(self, wb=None, zf=False):
        wb_info = {}
        wb_info['text'] = self.wb_text(wb, zf)
        wb_info['img'] = self.wb_img(wb, zf)
        wb_info['uid'] = self.wb_uid(wb, zf)
        wb_info['mid'] = self.wb_mid(wb, zf)
        wb_info['name'] = self.wb_name(wb, zf)
        wb_info['time_at'] = self.wb_time(wb, zf)
        wb_info['favorite'] = self.wb_favorite(wb, zf)
        wb_info['forward'] = self.wb_forward(wb, zf)
        wb_info['repeat'] = self.wb_repeat(wb, zf)
        wb_info['praised'] = self.wb_praised(wb, zf)
        return wb_info

    def wb_all_jiexi2(self, wb_detail):
        for wb in wb_detail:
            # 初始化wb 信息
            self.wb(wb)
            is_zf = self.is_zf_wb()
            wb_info = self.get_wb_info(wb, False)
            if is_zf:
                wb_info.setdefault('is_zf', is_zf)
                zf_wb = self.get_wb_info(wb, True)
                zf_wb.setdefault('pa_mid', wb_info.get('mid'))
                wb_info.setdefault('zf_wb', zf_wb)
                wb_info.setdefault('zf_mid', zf_wb.get('mid', None))
            self.weibodata.append(wb_info)
        return self.weibodata

    def jiexi2(self, content=None):
        if content is None:
            raise exception.NotFoundContent()

        if six.PY3:
            content = content.decode('utf-8')

        content = self.tmp_file(content)
        wb_detail = self.wb_detail(content)
        if not len(wb_detail):
            raise exception.DetailNotFound()

        return self.wb_all_jiexi2(wb_detail)
