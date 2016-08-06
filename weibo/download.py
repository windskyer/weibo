# --*-- coding: utf-8 --*--
# author: zwei
# email: suifeng20@hotmail.com

''' Download specifild img/videos URL '''

import os
import urllib2
import urlparse

from weibo import utils
from weibo import exception
from weibo.common import cfg
from weibo.common import log as logging
from weibo.db.api import db_api
from weibo.common.gettextutils import _

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class Download(object):
    def __init__(self, url=None, zf=False):
        if not url:
            self.urls = []
        else:
            if isinstance(url, str):
                self.urls = [url]
            elif isinstance(url, list):
                self.urls = url
            else:
                raise exception.UrlsNotUser(urls=self.urls)
        self.image_dir = CONF.image_dir or self.imagedir()
        self.ts = CONF.enable_multitargets

    def imagedir(self, name=None):
        if not name:
            imagedir = os.path.join(os.path.dirname(__file__),
                                    'image')
        else:
            imagedir = os.path.join(os.path.dirname(__file__),
                                    'image',
                                    name[1:])
        imagedir = os.path.abspath(imagedir)
        if not os.path.exists(imagedir):
            os.makedirs(imagedir, 0o777)
        return imagedir

    def get_all_urls(self, mid):
        pass

    def get_all_urls_zf(self, mid):
        pass

    def get_img(self, url):
        try:
            conn = urllib2.urlopen(url)
        except:
            raise exception.NotFoundImg(url=url)
        return conn

    def get_imgfile(self, url):
        name = urlparse.urlsplit(url).path
        path, imgfile = os.path.split(name)
        if imgfile:
            if CONF.image_dir:
                img_file = CONF.image_dir
            else:
                img_file = self.imagedir(path)
        imgfile = os.path.join(img_file, imgfile)
        return imgfile

    def save_img(self, conn, imgfile):
        LOG.debug(_('Saving imgfile to %s' % imgfile))
        with open(imgfile, 'wb') as fp:
            fp.write(conn.read())


class ImageDl(Download):

    def __init__(self, nickname=None):
        super(ImageDl, self).__init__()
        self.nickname = nickname
        self.names = []
        self.uids = []
        self.db_update = {}
        self.urls = {}

    @property
    def get_all_uid(self):
        for t in self.ts:
            self.names.append(CONF[t].nickname)
        for name in self.names:
            userdata = db_api.db_userdata_get_by_name(name)
            if userdata:
                self.uids.append(userdata.get('uid', None))

    @property
    def get_db_all_uid(self):
        values = db_api.db_userdata_get_all()
        for value in values:
            self.names.append(value.screen_name)
            self.uids.append(value.uid)

    def get_all_img_urls(self, uid):
        LOG.debug(_('Get all img url from wbimg table'))
        urls = []
        if db_api.is_wbimg_get_by_uid(uid):
            imgs = db_api.db_wbimg_get_by_uid(uid)
            for img in imgs:
                url = img.get('url', None)
                if not url:
                    continue
                urls.append(url)
        return urls

    def get_all_zfimg_urls(self, uid):
        LOG.debug(_('Get all img url from zfwbimg table'))
        urls = []
        if db_api.is_zfwbimg_get_by_uid(uid):
            zfimgs = db_api.db_zfwbimg_get_by_uid(uid)
            for zfimg in zfimgs:
                url = zfimg.get('url', None)
                if not url:
                    continue
                urls.append(url)
        return urls

    def exists_img(self, url):
        is_exists = False
        imgfile = self.get_imgfile(url)
        if os.path.exists(imgfile):
            is_exists = True
        return is_exists, imgfile

    def download(self, uid=None):
        urls = []
        zfurls = []
        if not uid:
            self.get_db_all_uid
        else:
            self.uids = [uid]

        for uid in self.uids:
            urls.extend(self.get_all_img_urls(uid))
            zfurls.extend(self.get_all_zfimg_urls(uid))

        self.urls['wb'] = urls
        self.urls['zfwb'] = zfurls
        for k, v in self.urls.items():
            for url in v:
                is_exists, imgfile = self.exists_img(url)
                if is_exists:
                    if k == 'zfwb':
                        self.update_to_db(url, imgfile, True)
                    if k == 'wb':
                        self.update_to_db(url, imgfile, False)
                    LOG.debug(_('img file  %s is exists' % imgfile))
                    continue
                try:
                    LOG.debug(_('Downloading img url %s' % url))
                    conn = self.get_img(url)
                except exception.NotFoundImg:
                    continue
                else:
                    self.save_img(conn, imgfile)
                    if k == 'zfwb':
                        self.update_to_db(url, imgfile, True)
                    if k == 'wb':
                        self.update_to_db(url, imgfile, False)

    def update_to_db(self, url, location, iszf=False):
        if not iszf:
            img = db_api.db_wbimg_get_by_url(url)
        else:
            img = db_api.db_zfwbimg_get_by_url(url)
        bigurl = utils.exists_big_img(url)
        if bigurl and img.bigurl is None:
            LOG.info(_('Updating bigurl to wbimg, zfwbimg'))
            img.bigurl = bigurl
        img.location = location
        img.save()


class VideosDl(Download):
    pass


def main():
    imagedl = ImageDl()
    imagedl.download()
