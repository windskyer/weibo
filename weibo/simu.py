# --*-- conding: utf-8 --*--
# Copyright (c) 2016

import os
# import eventlet

from weibo import exception
from weibo.db import api
from weibo.login import Login
from weibo.jhtml import Jhtml
from weibo.common import cfg
from weibo.common import log as logging

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class Dbsave(object):

    # weibo create
    def db_weibo_create(self, values):
        return api.weibo_create(values)

    # weibo update
    def db_weibo_update(self, values):
        return api.weibo_update(values)

    # weibo crate or update
    def db_weibo_create_or_update(self, values):
        is_exist = self.db_is_weibo_get_by_mid(values['mid'])
        if is_exist:
            self.db_weibo_update(values)
        else:
            self.db_weibo_create(values)

    # get mid from weibo db
    def db_is_weibo_get_by_mid(self, mid):
        try:
            api.weibo_get_by_mid(mid)
        except exception.WeiboMidNotFound:
            return False
        return True

    # wbtext create
    def db_wbtext_create(self, values):
        return api.wbtext_create(values)

    # wbtext update
    def db_wbtext_update(self, values):
        return api.wbtext_update(values)

    # wbtext crate or update
    def db_wbtext_create_or_update(self, values):
        is_exist = self.db_is_wbtext_get_by_mid(values['mid'])
        if is_exist:
            return
            self.db_wbtext_update(values)
        else:
            self.db_wbtext_create(values)

    # get mid from weibo db
    def db_is_wbtext_get_by_mid(self, mid):
        try:
            api.wbtext_get_by_mid(mid)
        except exception.WbtextMidNotFound:
            return False
        return True

    # wbimg create
    def db_wbimg_create(self, values):
        return api.wbimg_create(values)

    # wbing update
    def db_wbimg_update(self, values):
        return api.wbimg_update(values)

    # wbimg crate or update
    def db_wbimg_create_or_update(self, values):
        is_exist = self.db_is_wbimg_get_by_url(values['url'])
        if is_exist:
            return
            self.db_wbimg_update(values)
        else:
            self.db_wbimg_create(values)
    # get url from weibo db
    def db_is_wbimg_get_by_url(self, url):
        try:
            api.wbimg_get_by_url(url)
        except exception.WbimgUrlNotFound:
            return False
        return True

    # get mid from weibo db
    def db_is_wbimg_get_by_mid(self, mid):
        try:
            api.wbimg_get_by_mid(mid)
        except exception.WbimgMidNotFound:
            return False
        return True

    # save all data to db
    def save_all_data(self):
        pass

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

    @property
    def get_urls_name(self):
        targets = CONF.enable_multitargets
        t_url = {}
        if isinstance(targets, list):
            for target in targets:
                t_url['nickname'] = CONF[target].nickname
                t_url['url'] = CONF[target].url
                self.targets.append(t_url)

        if isinstance(targets, str):
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

    @classmethod
    def check_login(cls):
        cls.set_env()
        if not os.path.exists(cls.cookie_file):
            print("weibo login is reset")
            cls.pre_weibo_login()
        return 0

    @classmethod
    def pre_weibo_login(cls):
        cls.login = Login(cls.username, cls.password)

    def get_content(self, url):
        content = self.login.getHTML(url)
        self.jhtml(content)
        return self.jhtml.weibodata

    def detail(self, url=None):
        if not url:
            url = self.urls

        if isinstance(url, str):
            nickname = self.get_nickname(url)
            self.weibodata[nickname] = self._detail(url)

        if isinstance(url, list):
            for u in url:
                nickname = self.get_nickname(u)
                self.weibodata[nickname] = self._detail(u)

        return self.weibodata

    def _detail(self, url=None):
        if url:
            return self.get_content(url)

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

        time_at = weibodata.get('time', None)
        values.setdefault('time_at', time_at)

        return values

    def get_wbtext_data(self, weibodata):
        values = {}
        texts = []
        mid = weibodata.get('mid', None)
        values.setdefault('mid', mid)

        uid = weibodata.get('uid', None)
        values.setdefault('uid', uid)

        text = weibodata.get('text', None)
        values.setdefault('text', text.get('text', None))
        values.setdefault('is_zf', text.get('is_zf', None))

        face = weibodata.get('face', None)
        values.setdefault('face', face)

        url = weibodata.get('url', None)
        values.setdefault('url', url)

        zf_mid = weibodata.get('zf_mid', None)
        values.setdefault('zf_mid', zf_mid)

        return values

    def get_wbimg_data(self, weibodata):
        values = {}
        mid = weibodata.get('mid', None)
        values.setdefault('mid', mid)

        uid = weibodata.get('uid', None)
        values.setdefault('uid', uid)

        zf_mid = weibodata.get('zf_mid', None)
        values.setdefault('zf_mid', zf_mid)

        img = weibodata.get('img', None)
        if img:
            urls = img.get('urls', None)
            values.setdefault('urls', urls)

            is_zf = img.get('is_zf', False)
            values.setdefault('is_zf', is_zf)

        return values

    def save_weibo(self, weibodata=None):
        weibo = self.get_weibo_data(weibodata)
        self.db_weibo_create_or_update(weibo)

    def save_wbtext(self, weibodata=None):
        wbtext = self.get_wbtext_data(weibodata)
        self.db_wbtext_create_or_update(wbtext)
        zf_wb = self.get_zf_wb(weibodata)
        if zf_wb:
            zf_wb_text = self.get_wbtext_data(zf_wb)
            self.db_wbtext_create_or_update(zf_wb_text)

    def save_wbimg(self, weibodata=None):
        wbimg = self.get_wbimg_data(weibodata)
        if wbimg.has_key('urls'):
            for url in wbimg.pop('urls'):
                wbimg['url'] = url
                self.db_wbimg_create_or_update(wbimg)
                #self.db_wbimg_create(wbimg)

        zf_wb = self.get_zf_wb(weibodata)
        if zf_wb:
            zf_wb_img = self.get_wbimg_data(zf_wb)
            if zf_wb_img.has_key('urls'):
                for url in zf_wb_img.pop('urls'):
                    zf_wb_img['url'] = url
                    self.db_wbimg_create_or_update(zf_wb_img)

    def save_data(self, weibodatas=None):
        for weibodata in weibodatas:
            self.save_weibo(weibodata)
            self.save_wbtext(weibodata)
            self.save_wbimg(weibodata)

    def save_all_data(self):
        values = self.weibodata
        for nickname, data in values.items():
            print(nickname)
            self.save_data(data)
