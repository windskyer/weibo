# --*-- coding: utf-8 --*--
import urlparse

from weibo import utils
from weibo import version
from weibo import exception
from weibo.api import api
from weibo.db import api as db_api
from weibo.common import cfg
from weibo.common.gettextutils import _
from weibo.common import log as logging
from weibo.common import timeutils

CONF = cfg.CONF
LOG = logging.getLogger(__name__)

_CACHED_JSON = {}


class Userdata(db_api.Dbsave):
    def __init__(self, ts=None):
        if not ts:
            self.ts = CONF.enable_multitargets
        self.api_num = 0
        self.api_key = CONF.api_key

        self.nicknames = []
        self.get_userapi()
        self.get_all_names_json()

    def get_users_from_json(self, filename=None):
        self.nicknames = []
        if not filename:
            filename = CONF.user_json
        return utils.read_cached_file(filename, _CACHED_JSON)

    def get_all_names_json(self, delete=False):
        userdict = self.get_users_from_json()
        if 'users' in userdict:
            for user in userdict['users']:
                nickname = user.get('nickname')
                delete = eval(user.get('delete', delete))
                if delete:
                    self.remove_userdate_by_name(nickname)
                if nickname and not delete:
                    self.nicknames.append(nickname)

    def get_userapi(self, rm=False):
        if isinstance(self.api_key, list) and self.api_num < len(self.api_key):
            api_key = self.api_key[self.api_num]
        else:
            api_key = self.api_key
        LOG.info(_('use api key info %s' % api_key))
        self.userapi = api.useAPI(CONF[api_key], rm)
        self.api_num = self.api_num + 1

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

    def remove_userdate_by_name(self, nickname):
        try:
            self.db_userdata_delete_name(nickname)
        except exception.UserdataNameNotFound:
            pass

    def remove_userdata(self):
        udatas = self.db_userdata_get_all()
        for udata in udatas:
            nickname = udata.screen_name
            if isinstance(nickname, unicode):
                nickname = nickname.encode('utf-8')
            if nickname not in self.nicknames:
                LOG.debug('Deleted nickname %s' % nickname)
                udata.delete()

    def call(self, url=None, **kwargs):
        try:
            result = self.userapi.get(url, **kwargs)
        except RuntimeError:
            self.get_userapi(rm=True)
            result = self.userapi.get(url, **kwargs)
        return result

    def get_user_show(self, screen_name=None):
        if not screen_name:
            raise exception.NicknameNotNull()
        return self.call('users/show', screen_name=screen_name)

    def get_user_counts(self, uid):
        if not uid:
            raise exception.UidNotNull()
        return self.call('users/counts', uids=uid)

    def get_user_domain(self, domain):
        return
        if not domain:
            return
            raise exception.DomainNotNull()
        return self.call('users/domain_show', domain=domain)

    def _get_all_values(self, ushow, ucount, domain):
        values = {}
        values['uid'] = ushow.get('id')
        values['name'] = ushow.get('name')
        values['screen_name'] = ushow.get('screen_name')
        values['location'] = ushow.get('location')
        # values['description'] = ushow.get('description')
        values['profile_image_url'] = ushow.get('profile_image_url')
        if isinstance(ucount, list):
            ucount = ucount[0]
        values['friends_count'] = ucount.get('friends_count')
        values['followers_count'] = ucount.get('followers_count')
        values['ability_tags'] = ushow.get('ability_tags')
        values['gender'] = ushow.get('gender')
        values['urank'] = ushow.get('urank')
        values['credit_score'] = ushow.get('credit_score')
        values['created_at'] = timeutils.convert_dt(ushow.get('created_at'))
        values['profile_url'] = ushow.get('profile_url')
        values['homepage'] = self.set_homepage(ushow.get('profile_url'))
        # values['verified_reason'] = ushow.get('verified_reason')
        values['verified'] = ushow.get('verified')
        # values['remark'] = ushow.get('remark')
        return values

    def set_homepage(self, profile_url=None):
        if not profile_url:
            return
        homepage = urlparse.urljoin(version.WEIBOWEB_HOME, profile_url)
        return homepage

    def get_all_valuses(self, nickname):
        u1 = self.get_user_show(nickname)
        uid = u1.get('id', None)
        u2 = self.get_user_counts(uid)
        domain = u1.get('domain', None)
        u3 = self.get_user_domain(domain)
        return self._get_all_values(u1, u2, u3)

    def save_one_user(self, nickname):
        values = self.get_all_valuses(nickname)
        if values:
            self.db_userdata_create_or_update(values)

    def save_all_users(self):
        # self.remove_userdata()
        if isinstance(self.nicknames, list):
            for nickname in self.nicknames:
                self.save_one_user(nickname)
        else:
            self.save_one_user(self.nicknames)


class Huserdata(db_api.Dbsave):
    def get_html(self):
        pass
