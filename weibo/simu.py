# --*-- coding: utf-8 --*--
# Copyright (c) 2016

import os
import six

from weibo import exception
from weibo.db.api import Dbsave
from weibo.login import Login
from weibo.jhtml import Jhtml
from weibo.common import cfg
from weibo.common import log as logging
from weibo.common.gettextutils import _

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class Simu(Dbsave):
    """ frist login weibo """
    username = "unkown"
    password = "unkown"
    cookie_file = "/tmp/weibo_login_cookies.dat"
    login = None

    def __init__(self):
        self.username = CONF.username
        self.password = CONF.password
        self.cookie_file = CONF.cookie_file
        self.urls = []
        self.nickname = []
        self.weibodata = {}
        self.targets = []
        self.mutliusers = CONF.enable_multiusers
        self.get_urls_name
        self.get_urls
        self.get_nicknames
        self.login = Login(self.username, self.password)
        self.jhtml = Jhtml()
        self.exist_weibodata = []

    @property
    def get_urls_name(self):
        targets = CONF.enable_multitargets
        if isinstance(targets, list):
            for target in targets:
                t_url = {}
                t_url['nickname'] = CONF[target].nickname
                t_url['url'] = CONF[target].url
                self.targets.append(t_url)

        if isinstance(targets, str):
            t_url = {}
            t_url['nickname'] = CONF[targets].nickname
            t_url['url'] = CONF[targets].url
            self.targets.append(t_url)

    @property
    def get_urls(self):
        for target in self.targets:
            self.urls.append(target.get('url'))

    @property
    def get_nicknames(self):
        for target in self.targets:
            self.nickname.append(target.get('nickname'))

    def get_nickname(self, url):
        for t_url in self.targets:
            if t_url.get('url') == url:
                nickname = t_url.get('nickname')
                break
        return nickname

    def get_url(self, nickname):
        for t_url in self.targets:
            if t_url.get('nickname') == nickname:
                url = t_url.get('url')
                break
        return url

    @classmethod
    def set_env(cls):
        cls.username = CONF.username
        cls.password = CONF.password
        cls.cookie_file = CONF.cookie_file
        LOG.info("weibo set env username %(username)s "
                 "cookie_file %(cookie_file)s",
                 {'username': cls.username,
                  'cookie_file': cls.cookie_file})

    @classmethod
    def reset_login(cls):
        if os.path.exists(cls.cookie_file):
            LOG.info("weibo login is reset change cookie_file")
            # os.remove(cls.cookie_file)

        cls.set_env()
        if not os.path.exists(cls.cookie_file):
            LOG.info("weibo login is reset")
            cls.pre_weibo_login()
        return 0

    @classmethod
    def check_login(cls):
        cls.set_env()
        if not os.path.exists(cls.cookie_file):
            LOG.info("weibo login is reset")
            cls.pre_weibo_login()
        return 0

    @classmethod
    def pre_weibo_login(cls):
        LOG.info("weibo pre login set env")
        cls.login = Login(cls.username, cls.password)

    def get_content(self, url):
        try:
            content = self.login.getHTML(url)
            self.jhtml(content)
        except exception.DetailNotFound:
            self.login.cookie_file(content)
            content = self.login.getHTML(url)
            self.jhtml(content)
        return self.jhtml.weibodata

    def detail(self, url=None, is_db=False, nickname=None):
        if not url:
            url = self.urls

        if isinstance(url, six.string_types):
            url = [url]

        if isinstance(url, list):
            for u in url:
                if not is_db or not nickname:
                    nickname = self.get_nickname(u)

                LOG.info(_('Get %(nickname)s user weibo info url is %(url)s'),
                         {'nickname': nickname, 'url': u})
                self.weibodata[nickname] = self._detail(u)

        weibodata = self.weibodata
        return weibodata

    # get all name info from userdata
    def get_db_userdata_all(self):
        udata = self.db_userdata_get_all()
        return udata

    # 使用多线成对一个 大号处理
    def eventlet_one_url(self, url, nickname):
        if nickname not in self.exist_weibodata:
            LOG.info(_("updating %(nickname)s from %(url)s"),
                     {'nickname': nickname,
                      'url': url}
                     )
            self.exist_weibodata.append(nickname)
            try:
                weibodata = self.detail(url, True, nickname)
            except exception.DetailNotFound:
                LOG.error(_('reset login weibo use athors weibo user,password'))
                try:
                    self.reset_login(nickname)
                except:
                    raise exception.ResetLoginError()
            else:
                self.exist_weibodata.remove(nickname)
                self.save_all_data(weibodata)
        else:
            LOG.warn(_("not updating %(nickname)s from %(url)s"),
                     {'nickname': nickname,
                      'url': url}
                     )

    def _detail(self, url=None):
        if url:
            LOG.info(_('get all weibo info from %(url)s'),
                     {'url': url})
            return self.get_content(url)
        else:
            LOG.exception(_('Not Found url'))

    def get_zf_wb(self, weibodata=None):
        return weibodata.get('zf_wb', None)

    def get_weibo_data(self, weibodata):
        values = {}
        mid = weibodata.get('mid', None)
        values.setdefault('mid', mid)

        uid = weibodata.get('uid', None)
        values.setdefault('uid', uid)

        forward = weibodata.get('forward', 0)
        values.setdefault('forward', forward)

        repeat = weibodata.get('repeat', 0)
        values.setdefault('repeat', repeat)

        praised = weibodata.get('praised', 0)
        values.setdefault('praised', praised)

        time_at = weibodata.get('time_at', None)
        values.setdefault('time_at', time_at)

        return values

    def get_wbtext_data(self, weibodata, iszf=False):
        values = {}
        mid = weibodata.get('mid', None)
        values.setdefault('mid', mid)

        uid = weibodata.get('uid', None)
        values.setdefault('uid', uid)

        text = weibodata.get('text', None)
        values.setdefault('text', text.get('text', None))
        is_zf = weibodata.get('is_zf', None)
        if not is_zf:
            is_zf = text.get('is_zf', False)

        values.setdefault('is_zf', is_zf)

        face = weibodata.get('face', None)
        values.setdefault('face', face)

        url = weibodata.get('url', None)
        values.setdefault('url', url)

        if iszf:
            pa_mid = weibodata.get('pa_mid', None)
            values.setdefault('pa_mid', pa_mid)
        else:
            zf_mid = weibodata.get('zf_mid', None)
            values.setdefault('zf_mid', zf_mid)

        return values

    def get_wbimg_data(self, weibodata, iszf=False):
        values = {}
        mid = weibodata.get('mid', None)
        values.setdefault('mid', mid)

        uid = weibodata.get('uid', None)
        values.setdefault('uid', uid)

        is_zf = weibodata.get('is_zf', None)

        if iszf:
            pa_mid = weibodata.get('pa_mid', None)
            values.setdefault('pa_mid', pa_mid)
        else:
            zf_mid = weibodata.get('zf_mid', None)
            values.setdefault('zf_mid', zf_mid)

        img = weibodata.get('img', None)
        if img:
            urls = img.get('urls', None)
            values.setdefault('urls', urls)

            if not is_zf:
                is_zf = img.get('is_zf', False)
            values.setdefault('is_zf', is_zf)

        return values

    def save_weibo(self, weibodata=None):
        weibo = self.get_weibo_data(weibodata)
        self.db_weibo_create_or_update(weibo)

    def save_zfwbtext(self, zf_wb, iszf=True):
        zf_wbtext = self.get_wbtext_data(zf_wb, iszf)
        self.db_zfwbtext_create_or_update(zf_wbtext)

    def save_wbtext(self, weibodata=None):
        wbtext = self.get_wbtext_data(weibodata)
        self.db_wbtext_create_or_update(wbtext)
        zf_wb = self.get_zf_wb(weibodata)
        if zf_wb:
            self.save_zfwbtext(zf_wb)

    def save_zfwbimg(self, zf_wb=None, iszf=True):
        zf_wbimg = self.get_wbimg_data(zf_wb, iszf)
        if 'urls' in zf_wbimg.keys():
            urls = zf_wbimg.pop('urls')
            if urls:
                for url in urls:
                    zf_wbimg['url'] = url
                    self.db_zfwbimg_create_or_update(zf_wbimg)

    def save_wbimg(self, weibodata=None):
        wbimg = self.get_wbimg_data(weibodata)
        if 'urls' in wbimg.keys():
            urls = wbimg.pop('urls')
            if urls:
                for url in urls:
                    wbimg['url'] = url
                    self.db_wbimg_create_or_update(wbimg)

        zf_wb = self.get_zf_wb(weibodata)
        if zf_wb:
            self.save_zfwbimg(zf_wb)

    def save_data(self, weibodatas=None):
        for weibodata in weibodatas:
            self.save_weibo(weibodata)
            self.save_wbtext(weibodata)
            self.save_wbimg(weibodata)

    def save_all_data(self, weibodata=None):
        if not weibodata:
            values = self.weibodata
        else:
            values = weibodata
        for nickname, data in values.items():
            self.save_data(data)
