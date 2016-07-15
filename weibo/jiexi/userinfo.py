# --*-- coding: utf-8 --*--
import six
import re

from weibo.db import api
from weibo import exception
from weibo.jiexi import base
from weibo.common import cfg
from weibo.common import log as logging
from weibo.common.gettextutils import _

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


class Headinfo(api.Dbsave):

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

    def _jiexi_em(self, jx=None, attrs=None, is_em=False):
        attrs = {'class': attrs}
        try:
            j_em = self._get_children_tag(jx, name='em', attrs=attrs)
        except exception.NotFoundChildrenTag:
            return False
        else:
            if not is_em:
                return j_em
            else:
                return True

    def _jiexi_span(self, jx=None):
        attrs = {'location': 'W_ficon ficon_cd_place S_ficon',
                 'description': 'W_ficon ficon_pinfo S_ficon',
                 'domain': 'W_ficon ficon_link S_ficon',
                 'birthdate': 'W_ficon ficon_constellation S_ficon'}
        for key, value in attrs.items():
            if self._jiexi_em(jx=jx,
                              attrs=value,
                              is_em=True):
                return key
        return False

    def _jiexi_span_text(self, jx=None):
        span_info = jx.text
        return self._resolve_text(span_info)

    def _jiexi_span_em(self, jx=None):
        j_spans = jx.findAll('span')
        if len(j_spans) != 2:
            raise exception.NotDescription
        key = False
        value = None
        for j_span in j_spans:
            k = self._jiexi_span(j_span)
            if k:
                key = k
                continue
            if key:
                value = self._jiexi_span_text(j_span)
        return key, value

    def _jiexi_li(self, ul):
        person_info = {}
        lis = ul.findAll('li')
        for li in lis:
            try:
                attr, text = self._jiexi_span_em(li)
            except exception.NotDescription:
                continue
            if attr and text:
                person_info[attr] = text
        return person_info

    def _jiexi_ul(self, div=None):
        attrs = {'class': 'ul_detail'}
        if not div:
            return
        try:
            j_ul = self._get_children_tag(self.jperson.jx,
                                          name='ul',
                                          attrs=attrs)
        except exception.NotFoundChildrenTag:
            LOG.error(_('This weibo not fl'))
        else:
            return self._jiexi_li(j_ul)

    def person_description(self):
        attrs = {"class": "detail"}
        div = self._get_children_tag(self.jperson.jx,
                                     name='div',
                                     attrs=attrs)
        return self._jiexi_ul(div)

    def jiexi(self, j_person=None):
        udata = {}
        if j_person:
            jx = j_person
        else:
            jx = self.jperson.jx
        fl_info = self.person_fl_info(jx)
        udata['verified_reason'] = fl_info
        descr = self.person_description()
        udata['wb_descr'] = descr
        return udata

    def wb(self, WB):
        self.jperson(WB)
        return self.jiexi()

    def jiexi2(self, uid, content=None):
        if content is None:
            raise exception.NotFoundContent()
        if six.PY3:
            content = content.decode('utf-8')
        content = self.tmp_file(content)
        wb_person = self.wb_person(content)
        if not len(wb_person):
            raise exception.PersonNotFound()
        if isinstance(uid, six.string_types):
            uid = eval(uid)
        return self.jiexi2_and_save(uid, wb_person)

    def get_all_values(self, values):
        v = {}
        v['verified_reason'] = values.get('verified_reason', None)
        wb_descr = values.get('wb_descr', None)
        if wb_descr:
            v['birthdate'] = wb_descr.get('birthdate', None)
            v['description'] = wb_descr.get('description', None)
        return v

    def save_values_to_db(self, values, udata):
        if not udata['verified']:
            values['verified_reason'] = ''
        for k, v in values.items():
            udata[k] = v
        udata.save()

    def jiexi2_and_save(self, uid, WB):
        values = self.wb(WB)
        values = self.get_all_values(values)
        if self.is_userdata_get_by_uid(uid):
            udata = self.db_userdata_get_by_uid(uid)
            self.save_values_to_db(values, udata)
        return values


class Userinfo(Headinfo):

    def wb_head(self, content):
        # get all things from WB_person
        # WB_person = re.findall(r"PCD\_person\_info(.+?)PCD\_person\_info",
        #                       content)
        WB_head = content
        return WB_head

    def head_tmp_file(self, content):
        tmp = re.findall(r'pl\.header\.head\.'
                         r'index.*html\":\"(.*)\"}\)', content)
        for tmp_r in tmp:
            content = content.replace(tmp_r, 's')

        max = six.sys.maxint
        for i in tmp:
            if max > len(i):
                max = len(i)
                content = i

        content = content.replace('PCD_header',
                                  'PCD_headerPCD_header')
        return content

    def person_remark(self, jx=None):
        attrs = {"class": "pf_intro"}
        try:
            div = self._get_children_tag(self.jperson.jx,
                                         name='div',
                                         attrs=attrs)
        except exception.NotFoundChildrenTag:
            return
        else:
            return self._resolve_text(div.text)

    def h_jiexi(self, j_person=None):
        udata = {}
        if j_person:
            jx = j_person
        else:
            jx = self.jperson.jx
        remark = self.person_remark(jx)
        udata['remark'] = remark
        return udata

    def h_wb(self, WB):
        self.jperson(WB)
        return self.h_jiexi()

    def jiexi2(self, uid, content=None):
        if content is None:
            raise exception.NotFoundContent()
        if six.PY3:
            content = content.decode('utf-8')

        p_content = self.tmp_file(content)
        wb_person = self.wb_person(p_content)
        if not len(wb_person):
            raise exception.PersonNotFound()

        h_content = self.head_tmp_file(content)
        wb_head = self.wb_head(h_content)
        if not len(wb_head):
            raise exception.HeadNotFound()

        if isinstance(uid, six.string_types):
            uid = eval(uid)
        return self.jiexi2_and_save(uid, wb_person, wb_head)

    def get_all_values(self, values, h_values):
        v = {}
        v['verified_reason'] = values.get('verified_reason', None)
        wb_descr = values.get('wb_descr', None)
        if wb_descr:
            v['birthdate'] = wb_descr.get('birthdate', None)
            v['description'] = wb_descr.get('description', None)
        v['remark'] = h_values.get('remark', None)
        return v

    def jiexi2_and_save(self, uid, WB, H_WB):
        values = self.wb(WB)
        h_values = self.h_wb(H_WB)
        values = self.get_all_values(values, h_values)
        if self.is_userdata_get_by_uid(uid):
            udata = self.db_userdata_get_by_uid(uid)
            self.save_values_to_db(values, udata)
        return values
