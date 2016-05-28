# --*-- conding: utf-8 --*--
# Copyright (c) 2016

import os
# import eventlet

from weibo.login import Login
from weibo.common import cfg
from weibo.common import log

CONF = cfg.CONF


class Simu(object):
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
        self.webdata = {}
        self.targets = []
        self.mutliusers = CONF.enable_multiusers
        self.get_urls_name
        self.get_urls
        self.get_nicknames
        self.login = Login(self.username, self.password)

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

    def get_html(self, url):
        return self.login.getHTML(url)

    def detail(self, url=None):
        if not url:
            url = self.urls

        if isinstance(url, str):
            self.webdata[url] = self._detail(url)

        if isinstance(url, list):
            for u in url:
                self.webdata[u] = self._detail(u)

        return self.webdata

    def _detail(self, url=None):
        if url:
            # return jiexi(self.simu.getHTML(url))
            return self.get_html(url)
