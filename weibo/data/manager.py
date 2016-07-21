# --*-- coding: utf-8 --*--
import functools

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
    time = kwargs.get('time', 3)
    def outer(f):
        @functools.wraps(f)
        def inner(self, *args, **kw):
            if vm_state is not None and instance['vm_state'] not in vm_state:
                raise exception.InstanceInvalidState(
                    attr='vm_state',
                    instance_uuid=instance['uuid'],
                    state=instance['vm_state'],
                    method=f.__name__)
            if (task_state is not None and
                instance['task_state'] not in task_state):
                raise exception.InstanceInvalidState(
                    attr='task_state',
                    instance_uuid=instance['uuid'],
                    state=instance['task_state'],
                    method=f.__name__)

            return f(self, context, instance, *args, **kw)
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

    @periodic_task.periodic_task(spacing=CONF.weiboinfo_interval)
    def update_webo_info(self, **kwargs):
        udata = self.simulogin.get_db_userdata_all()
        for u in udata:
            nickname = u.get('screen_name', None)
            if nickname in self.exist_udata_name:
                continue
            self.exist_udata_name.append(nickname)
            url = u.get('homepage', None)
            # 设置微博每 10 分钟更新 一次
            tg = kwargs.get('tg', None)
            if not tg:
                return
            LOG.info(_LI('update %(nickname)s weibo info to db'),
                     {'nickname': nickname})
            tg.add_timer(300, self.update_one_weibo, 60, url, nickname)

    # 获取所有的用户的所有微博信息
    def get_all_user_all_weibo_info(self, *args, **kwargs):
        is_all = CONF.is_all
        if not is_all:
            return
        users = db_api.db_userdata_get_all()
        for user in users:
            homepage = user.homepage + '?is_all=1'
            nickname = user.nickname
            self.get_all_page_one_user_weibo_info(homepage)
            tg = kwargs.get('tg', None)
            if not tg:
                tg = self.tg

            LOG.info(_LI('get %(nickname)s weibo %(homepage)s info to db'),
                     {'nickname': nickname,
                      'homepage': homepage})
            if isinstance(tg, utils.LoopingCall):
                pass
            else:
                tg.add_thread(self.get_all_page_one_user_weibo_info,
                              *args,
                              **kwargs)

    def get_all_page_one_user_weibo_info(self, *args, **kwargs):
        if 'homeage' not in kwargs:
            raise
        else:
            homepage = kwargs.get('homeage')
        nickname = kwargs.get('nickname')
        page = kwargs.pop('page', 1)
        while True:
            url = homepage + '&page=%s' % page
            self.get_one_weibo(url, nickname)

    @wrap_time_exec(time=CONF.time)
    def _get_one_weibo(self, url, name):
        while time > 0:
            try:
                self.simulogin.eventlet_one_url(url, name)
            except exception.ResetLoginError:
                self.reset_login_weibo
                time = time - 1
            else:
                break

    def get_one_weibo(self, url, name):
            return
