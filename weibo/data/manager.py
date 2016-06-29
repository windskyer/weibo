# --*-- coding: utf-8 --*--
from weibo import simu
from weibo import userdata
from weibo import download
from weibo import manager
from weibo import exception
from weibo.common import cfg
from weibo.common import periodic_task
from weibo.common.gettextutils import _LI
from weibo.common import log as logging

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


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

    # 设置周期任务 14400s  每天更新4次
    @periodic_task.periodic_task(spacing=14400)
    def update_userdata_info(self, **kwargs):
        LOG.info(_LI('update userdata info to db'))
        self.udata.save_all_users()

    # 设置微博每 10 分钟更新 一次
    @periodic_task.periodic_task(spacing=600)
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

    @periodic_task.periodic_task(spacing=2)
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
