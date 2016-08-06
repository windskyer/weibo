# --*-- coding: utf-8 --*--
# Copyright (c) 2016

import os
import six
import time
import functools
import eventlet
import urllib2
import urlparse

from weibo import utils
from weibo import exception
from weibo.db.api import Dbsave
from weibo.login import Login
from weibo.jhtml import Jhtml
from weibo.common import cfg
from weibo.common import log as logging
from weibo.common import timeutils
from weibo.common.gettextutils import _, _LI

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


def wrap_time_exec(*args, **kwargs):
    ntime = kwargs.get('ntime', 10)
    if not ntime:
        ntime = 10

    def outer(f):
        @functools.wraps(f)
        def inner(self, *args, **kw):
            f.ntime = ntime
            n = 1
            while n <= f.ntime:
                LOG.debug(_LI('Execing %s time fucntin %s' % (n, f.__name__)))
                if n == f.ntime:
                    return f(self, *args, **kw)
                try:
                    return f(self, *args, **kw)
                except Exception:
                    n = n + 1
                    eventlet.greenthread.sleep(60)
        return inner
    return outer


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
        self.weibopc_exist_exec = []

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
        else:
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
        content = self.login.getHTML(url)
        try:
            self.jhtml(content)
        except exception.DetailNotFound:
            self.login.save_cookie(content)
            content = self.login.getHTML(url)
            self.jhtml(content)
        return self.jhtml.weibodata_dict

    def detail(self, url=None, is_db=False, nickname=None):
        if not url:
            url = self.urls

        if isinstance(url, six.string_types):
            url = [url]

        if isinstance(url, list):
            for u in url:
                save_weibodata = {}
                if not is_db or not nickname:
                    time.sleep(20)
                    nickname = self.get_nickname(u)
                    if nickname in self.weibopc_exist_exec:
                        continue

                self.weibodata[nickname] = self._detail(u)
                save_weibodata[nickname] = self.weibodata[nickname]
                LOG.info(_('Get %(nickname)s user weibo info url is %(url)s'),
                         {'nickname': nickname, 'url': u})
                if not is_db or not nickname:
                    self.weibopc_exist_exec.append(nickname)
                    self.save_all_data(save_weibodata)

        weibodata = self.weibodata
        return weibodata

    # get all name info from userdata
    def get_db_userdata_all(self):
        udata = self.db_userdata_get_all()
        return udata

    # get all page persifiled url
    def get_one_page_url(self, url, nickname):
        try:
            LOG.info(_("Geting %(nickname)s from %(url)s in this page"),
                     {'nickname': nickname,
                      'url': url}
                     )
            weibodata = self.detail(url, True, nickname)
        except exception.DetailNotFound:
            raise exception.ResetLoginError()
        except exception.DetailEmptyFound:
            raise exception.WeiboEnd
        else:
            self.save_all_data(weibodata)

    # 使用多线成对一个 大号处理
    @wrap_time_exec(ntime=CONF.ntime)
    def _eventlet_one_url(self, url, nickname):
        try:
            weibodata = self.detail(url, True, nickname)
            eventlet.greenthread.sleep(20)
        except exception.DetailNotFound:
            LOG.warn(_('reset login weibo use athors weibo user,password'))
            try:
                self.reset_login(nickname)
            except:
                raise exception.ResetLoginError()
        return weibodata

    def eventlet_one_url(self, url, nickname):
        if nickname not in self.exist_weibodata:
            LOG.info(_("updating %(nickname)s from %(url)s"),
                     {'nickname': nickname,
                      'url': url}
                     )
            self.exist_weibodata.append(nickname)
            try:
                weibodata = self._eventlet_one_url(url, nickname)
            except exception.ResetLoginError:
                raise
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

        datetime_at = timeutils.timestamp2datetime(time_at)
        values.setdefault('datetime_at', datetime_at)

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

    def exists_big_img(self, url):
        jxurl = urlparse.urlparse(url)
        path = jxurl.path
        netloc = jxurl.netloc
        dirname, filename = os.path.split(path)
        baseurl = jxurl.scheme + '://' + netloc
        if 'sinaimg' in netloc:
            dirname = '/mw690'
            path = dirname + '/' + filename
            bigurl = urlparse.urljoin(baseurl, path)
            try:
                urllib2.urlopen(bigurl)
            except Exception:
                return
            else:
                return bigurl

    def save_zfwbimg(self, zf_wb=None, iszf=True):
        zf_wbimg = self.get_wbimg_data(zf_wb, iszf)
        if 'urls' in zf_wbimg.keys():
            urls = zf_wbimg.pop('urls')
            if urls:
                for url in urls:
                    zf_wbimg['url'] = url
                    bigurl = utils.exists_big_img(url)
                    if bigurl:
                        zf_wbimg['bigurl'] = bigurl
                    self.db_zfwbimg_create_or_update(zf_wbimg)

    def save_wbimg(self, weibodata=None):
        wbimg = self.get_wbimg_data(weibodata)
        if 'urls' in wbimg.keys():
            urls = wbimg.pop('urls')
            if urls:
                for url in urls:
                    wbimg['url'] = url
                    bigurl = self.exists_big_img(url)
                    if bigurl:
                        wbimg['bigurl'] = bigurl
                    self.db_wbimg_create_or_update(wbimg)

        zf_wb = self.get_zf_wb(weibodata)
        if zf_wb:
            self.save_zfwbimg(zf_wb)

    def save_userdata(self, nickname, values):
        if self.is_userdata_get_by_name(nickname):
            userdata = self.db_userdata_get_by_name(nickname)
            userdata.verified_reason = values.get('verified_reason')
            wb_descr = values.get('wb_descr', None)
            if wb_descr:
                userdata.description = wb_descr.get('description')
                userdata.birthdate = wb_descr.get('birthdate')
                userdata.remark = wb_descr.get('remark')
            userdata.save()

    def save_data(self, nickname, weibodatas=None):
        for weibodata in weibodatas['weibodata']:
            self.save_weibo(weibodata)
            self.save_wbtext(weibodata)
            self.save_wbimg(weibodata)
        # userdata = weibodatas['userdata']
        # self.save_userdata(nickname, userdata)

    def save_all_data(self, weibodata=None):
        if not weibodata:
            values = self.weibodata
        else:
            values = weibodata
        for nickname, data in values.items():
            self.save_data(nickname, data)
