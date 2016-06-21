# --*-- coding: utf-8 --*--
# author: zwei
# email: suifeng20@hotmail.com

''' Download specifild img/videos URL '''

import os
import urllib2
import urlparse

from weibo import exception
from weibo.common import cfg
from weibo.common import log as logging
from weibo.db.api import db_api

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
        self.image_dir = CONF.image_dir or self.imagedir
        self.ts = CONF.enable_multitargets

    @property
    def imagedir(self):
        imagedir = os.path.join(os.path.dirname(__file__),
                                'image')
        imagedir = os.path.abspath(imagedir)
        if not os.path.exists(imagedir):
            os.mkdir(imagedir, 0o777)
        return imagedir

    def get_all_urls(self, mid):
        pass

    def get_all_urls_zf(self, mid):
        pass

    def get_img(self, url):
        try:
            name = urlparse.urlsplit(url).path
            conn = urllib2.urlopen(url)
        except:
            raise exception.NotFoundImg(url=url)
        return (conn, name)

    def save_img(self, conn, name):
        img_file = self.image_dir + name
        with open(img_file, 'wb') as fp:
            fp.write(conn.read())


class ImageDl(Download):

    def __init__(self, nickname=None):
        self.nickname = nickname
        self.names = []
        self.uids = []
        super(ImageDl, self).__init__()

    @property
    def get_all_uid(self):
        for t in self.ts:
            self.names.append(CONF[t].nickname)
        for name in self.names:
            userdata = db_api.db_userdata_get_by_name(name)
            if userdata:
                self.uids.append(userdata.get('uid', None))

    def get_all_img_urls(self, uid):
        imgs = db_api.db_wbimg_get_by_uid(uid)
        for img in imgs:
            url = img.get('url', None)
            if not url:
                continue
            self.urls.extend(url)

    def get_all_zfimg_urls(self, uid):
        zfimgs = db_api.db_zfwbimg_get_by_uid(uid)
        for zfimg in zfimgs:
            url = zfimg.get('url', None)
            if not url:
                continue
            self.urls.extend(url)

    def download(self):
        self.get_all_uid
        for uid in self.uids:
            self.get_all_img_urls(uid)
        for url in self.urls:
            conn, name = self.get_img(url)
            self.save_img(conn, name)


class VideosDl(Download):
    pass


def main():
    imagedl = ImageDl()
    imagedl.download()
