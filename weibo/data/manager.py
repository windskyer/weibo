# --*-- coding: utf-8 --*--
from weibo import userdata
from weibo import download
from weibo import manager
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

    # 设置周期任务 100s
    @periodic_task.periodic_task(spacing=200)
    def update_userdata_info(self):
        LOG.info(_LI('update userdata info to db'))
        self.udata.save_all_data()

    @periodic_task.periodic_task(spacing=1000)
    def download_all_img(self):
        LOG.info(_LI('download all img to db'))
        self.imagedl.download()
