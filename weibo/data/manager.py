# --*-- coding: utf-8 --*--
import os
import time
import functools
import eventlet

from weibo import simu
from weibo import userdata
from weibo import download
from weibo import manager
from weibo import utils
from weibo import exception
from weibo.common import cfg
from weibo.db.api import db_api
from weibo.common import periodic_task
from weibo.common.gettextutils import _LI
from weibo.common import log as logging

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


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


class Wbmanager(manager.Manager):
    """ weibo manager """
    def __init__(self, host=None, *args, **kwargs):
        super(Wbmanager, self).__init__(host, 'weibo')
        self.udata = userdata.Userdata()
        self.imagedl = download.ImageDl()
        # 首先登入
        simu.Simu.check_login()
        # 模拟登陆的功能扩展待完善
        self.simulogin = simu.Simu()
        self.exist_udata_name = []
        self.tg = kwargs.get('tg', utils.LoopingCall)
        self.is_all_and_runing = False

    def init_host(self, tg, **kwargs):
        LOG.info(_LI('Willing init  host function.......'))
        if CONF.is_all:
            pid = os.fork()
            if pid == 0:
                child_started = False
                while True:
                    enable_spawn = kwargs.get('enable_spawn', True)
                    if enable_spawn:
                        eventlet.spawn(self.get_all_user_all_weibo_info,
                                       **kwargs)
                        child_started = True
                    else:
                        kwargs['tg'] = tg
                        self.get_all_user_all_weibo_info(**kwargs)
                        child_started = True
                    if not child_started:
                        break
                os._exit(2)

            LOG.debug(_LI('Started child %d' % pid))

    def init_host(self, tg, **kwargs):
        LOG.info(_LI('Willing init  host function.......'))
        if tg:
            kwargs['tg'] = tg
        self.get_all_user_all_weibo_info(**kwargs)

    # 设置周期任务 14400s  每天更新4次
    @periodic_task.periodic_task(spacing=CONF.userdata_interval)
    def update_userdata_info(self, **kwargs):
        LOG.info(_LI('update userdata info to db'))
        self.udata.save_all_users()

    # 设置微博每 10 分钟更新 一次
    @periodic_task.periodic_task(spacing=CONF.download_interval)
    def download_all_img(self, **kwargs):
        LOG.info(_LI('download all img to db'))
        self.imagedl.download()

    @property
    def reset_login_weibo(self):
        simu.Simu.reset_login()
        self.simulogin = simu.Simu()

    # 更新周期
    def update_one_weibo(self, url, name):
        try:
            self.simulogin.eventlet_one_url(url, name)
        except exception.ResetLoginError:
            self.reset_login_weibo
            eventlet.greenthread.sleep(10)

    @periodic_task.periodic_task(spacing=CONF.weiboinfo_interval)
    def update_webo_info(self, **kwargs):
        udata = self.simulogin.get_db_userdata_all()
        for u in udata:
            nickname = u.get('screen_name', None)
            if nickname in self.exist_udata_name:
                continue
            self.exist_udata_name.append(nickname)
            url = u.get('homepage', None)
            if 'is_all' not in url:
                url = url + '?is_all=1'
            # 设置微博每 10 分钟更新 一次
            tg = kwargs.get('tg', None)
            if not tg:
                return
            LOG.info(_LI('update %(nickname)s weibo info to db'),
                     {'nickname': nickname})
            tg.add_timer(300, self.update_one_weibo, 3, url, nickname)

    # 获取所有的用户的所有微博信息
    @periodic_task.periodic_task
    def get_all_user_all_weibo_info(self, *args, **kwargs):
        if self.is_all_and_runing:
            return
        else:
            self.is_all_and_runing = True

        if not CONF.is_all:
            return

        users = db_api.db_userdata_get_all()
        tg = kwargs.pop('tg', None)
        for user in users:
            homepage = user.homepage
            nickname = user.screen_name
            LOG.info(_LI('get %(nickname)s weibo %(homepage)s info to db'),
                     {'nickname': nickname,
                      'homepage': homepage})
            kwargs['homepage'] = homepage
            kwargs['nickname'] = nickname
            try:
                if not tg:
                    self.get_all_page_one_user_weibo_info(**kwargs)
                else:
                    tg.add_thread(self.get_all_page_one_user_weibo_info,
                                  *args,
                                  **kwargs)
            except Exception:
                self.is_all_and_runing = False

    def get_all_page_one_user_weibo_info(self, *args, **kwargs):
        if 'homepage' not in kwargs:
            raise
        else:
            url = kwargs.get('homepage')
        self.get_one_weibo(url, **kwargs)

    @wrap_time_exec(ntime=CONF.ntime)
    def _get_one_weibo(self, url, name):
        self.simulogin.get_one_page_url(url, name)

    def get_url(self, url, page=1, **kwargs):
        return url + '?is_all=1' + '&page=%s' % page

    def get_one_weibo(self, url, **kwargs):
        nickname = kwargs.get('nickname')
        page = kwargs.get('page', 1)
        while True:
            try:
                self._get_one_weibo(self.get_url(url, page), nickname)
            except exception.ResetLoginError:
                self.reset_login_weibo
                kwargs['page'] = page
                self.get_one_weibo(url, **kwargs)
            except exception.WeiboEnd:
                return
            else:
                page = page + 1
                eventlet.greenthread.sleep(45)
