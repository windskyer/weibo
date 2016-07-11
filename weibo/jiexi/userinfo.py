# --*-- coding: utf-8 --*--
import six
import re

from weibo.db import api
from weibo import exception
from weibo.jiexi import base
from weibo.common import cfg
from weibo.common import log as logging

LOG = logging.getLogger(__name__)
CONF = cfg.CONF
JIEXI_TAG = 'PCD_person_info'


class JPerson(object):
    '''
    pasre WB_person info
    '''
    def __init__(self, *args, **kwargs):
        self.content = kwargs.get('content', None)
        self.jx = base.Soup()

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


class Userinfo(api.Dbsave):

    def __init__(self):
        self.jperson = JPerson()

    # 获取 正常的 text 文本信息
    def _resolve_text(self, text):
        if not isinstance(text, six.text_type):
            text = unicode(text, 'utf-8')
        return text.strip()

    def wb_person(self, content):
        # get all things from WB_person
        # WB_person = re.findall(r"PCD\_person\_info(.+?)PCD\_person\_info",
        #                       content)
        WB_person = content
        return WB_person

    def tmp_file(self, content):
        tmp = re.findall(r'pl\.content\.homeFeed\.'
                         r'index.*html\":\"(.*)\"}\)', content)
        for tmp_r in tmp:
            content = content.replace(tmp_r, 's')

        max = six.sys.maxint
        for i in tmp:
            if max > len(i):
                max = len(i)
                content = i

        content = content.replace('PCD_person_info',
                                  'PCD_person_infoPCD_person_info')
        return content

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

    def person_fl(self):
        attrs = {'class': "icon_bed W_fl"}
        try:
            self._get_children_tag(self.jperson.jx,
                                   name='span',
                                   attrs=attrs)
        except exception.NotFoundChildrenTag:
            LOG.warn(_('This weibo not fl'))
            return False
        return True

    def person_fl_info(self, jx=None):
        attrs = {'class': "info"}
        if self.person_fl():
            j_span = self._get_children_tag(self.jperson.jx,
                                            name='p',
                                            attrs=attrs)
            fl_info = j_span.text
            return self._resolve_text(fl_info)

    def _jiexi_ul_li(self, div=None):
        if not div:
            return
        pass

    def person_description(self):
        attrs = {"class": "detail"}
        div = self._get_children_tag(self.jperson.jx,
                                     name='div',
                                     attrs=attrs)
        return self._jiexi_ul_li(div)

    def jiexi(self, j_person=None):
        udata = {}
        if j_person:
            jx = j_person
        fl_info = self.person_fl_info(jx)
        udata['fl'] = fl_info
        descr = self.person_description()
        udata['wb_descr'] = descr
        return udata

    def wb(self, WB):
        self.jperson(WB)
        return self.jiexi()

    def jiexi2(self, content=None):
        # import pdb;pdb.set_trace()
        if content is None:
            raise exception.NotFoundContent()
        if six.PY3:
            content = content.decode('utf-8')
        content = self.tmp_file(content)
        wb_person = self.wb_person(content)
        if not len(wb_person):
            raise exception.PersonNotFound()
        return self.jiexi2_and_save(wb_person)

    def jiexi2_and_save(self, WB):
        values = self.wb(WB)
        return values
