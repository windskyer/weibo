# --*-- coding: utf-8 --*--

from weibo import exception
from weibo.db import api as db_api
from weibo.api import api
from weibo.common import cfg
from weibo.common import log as logging

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class Dbsave(object):

    def create_userdata(self, values):
        db_api.create_userdata(values)

    def update_userdata(self, values):
        db_api.update_userdata(values)

    def db_userdata_create_or_update(self, values):
        if self.is_userdata_get_by_uid(values.get('uid')):
            self.update_userdata(values)
        else:
            self.create_userdata(values)

    def is_userdata_get_by_uid(sefl, uid):
        try:
            db_api.userdata_get_by_name(uid)
        except exception.UserdataUidNotFound:
            return False
        return True


class Userdata(Dbsave):
    def __init__(self, ts=None):
        if not ts:
            self.ts = CONF.enable_multitargets
        self.api_key = CONF.api_key
        if isinstance(self.api_key, list):
            self.api_key = self.api_key[0]

        self.userapi = api.useAPI(CONF[self.api_key])
        self.nicknames = []
        self.get_all_names()

    def get_all_names(self):
        if isinstance(self.ts, list):
            for t in self.ts:
                nickname = CONF[t].nickname
                if nickname:
                    self.nicknames.append(nickname)

        if isinstance(self.ts, str):
            nickname = CONF[self.ts].nickname
            if nickname:
                self.nicknames.append(nickname)

    def call(self, url=None, **kwargs):
        return self.userapi.get(url, **kwargs)

    def get_user_show(self, screen_name=None):
        if not screen_name:
            raise exception.NicknameNotNull()
        return self.call('users/show', screen_name=screen_name)

    def get_user_counts(self, uid):
        if not uid:
            raise exception.UidNotNull()
        return self.call('users/counts', uids=uid)

    def get_all_valuses(self, nickname):
        u1 = self.get_user_show(nickname)
        uid = u1.get('id', None)
        u2 = self.get_user_counts(uid)
        #return u1.exten(u2)

    def save_one_user(self, nickname):
        values = self.get_all_valuses(nickname)
        self.db_userdata_create_or_update(values)

    def save_all_users(self):
        if isinstance(self.nicknames, list):
            for nickname in self.nicknames:
                self.save_one_user(nickname)
        else:
            self.save_one_user(self.nicknames)
