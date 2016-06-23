# --*-- coding; utf-8 --*--
# author: zwei
# email: suifeng20@hotmail.com

from weibo import exception
from weibo.db.sqlalchemy import api


class Dbsave(object):

    # userdata create
    def db_userdata_create(self, values):
        api.userdata_create(values)

    # userdata update
    def db_userdata_update(self, values):
        api.userdata_update(values)

    # userdata create or update
    def db_userdata_create_or_update(self, values):
        if self.is_userdata_get_by_uid(values.get('uid')):
            self.db_userdata_update(values)
        else:
            self.db_userdata_create(values)

    # is exists userdata by uid
    def is_userdata_get_by_uid(self, uid):
        try:
            api.userdata_get_by_uid(uid)
        except exception.UserdataUidNotFound:
            return False
        return True

    # get uid from userdata db
    def db_userdata_get_by_uid(self, uid):
        return api.userdata_get_by_uid(uid)

    # is exists userdata by id
    def is_userdata_get_by_id(self, id):
        try:
            api.userdata_get_by_id(id)
        except exception.UserdataIdNotFound:
            return False
        return True

    # get id from userdata db
    def db_userdata_get_by_id(self, id):
        return api.userdata_get_by_id(id)

    # is exists userdata by name
    def is_userdata_get_by_name(self, name):
        try:
            api.userdata_get_by_name(name)
        except exception.UserdataNameNotFound:
            return False
        return True

    # get name from userdata db
    def db_userdata_get_by_name(self, name):
        return api.userdata_get_by_name(name)

    # get all userdata by db
    def db_userdata_get_all(self):
        return api.userdata_get_all()

    # delete userdata by id
    def db_userdata_delete(self, id):
        if self.is_userdata_get_by_id(id):
            api.userdata_delete(id)

    # delete userdata by uid
    def db_userdata_delete_uid(self, uid):
        if self.is_userdata_get_by_uid(uid):
            api.userdata_delete_uid(uid)

    # delete userdata by name
    def db_userdata_delete_name(self, name):
        if self.is_userdata_get_by_name(name):
            api.userdata_delete_name(name)

    # weibo create
    def db_weibo_create(self, values):
        return api.weibo_create(values)

    # weibo update
    def db_weibo_update(self, values):
        return api.weibo_update(values)

    # weibo crate or update
    def db_weibo_create_or_update(self, values):
        is_exist = self.db_is_weibo_get_by_mid(values['mid'])
        if is_exist:
            self.db_weibo_update(values)
        else:
            self.db_weibo_create(values)

    # get mid from weibo db
    def db_is_weibo_get_by_mid(self, mid):
        try:
            api.weibo_get_by_mid(mid)
        except exception.WeiboMidNotFound:
            return False
        return True

    # wbtext create
    def db_wbtext_create(self, values):
        return api.wbtext_create(values)

    # wbtext update
    def db_wbtext_update(self, values):
        return api.wbtext_update(values)

    # wbtext crate or update
    def db_wbtext_create_or_update(self, values):
        is_exist = self.db_is_wbtext_get_by_mid(values['mid'])
        if is_exist:
            self.db_wbtext_update(values)
        else:
            self.db_wbtext_create(values)

    # get mid from weibo db
    def db_is_wbtext_get_by_mid(self, mid):
        try:
            api.wbtext_get_by_mid(mid)
        except exception.WbtextMidNotFound:
            return False
        return True

    # wbimg create
    def db_wbimg_create(self, values):
        return api.wbimg_create(values)

    # wbing update
    def db_wbimg_update(self, values):
        return api.wbimg_update(values)

    # wbimg crate or update
    def db_wbimg_create_or_update(self, values):
        is_exist = self.is_wbimg_get_by_url(values['url'])
        if is_exist:
            self.db_wbimg_update(values)
        else:
            self.db_wbimg_create(values)

    # get url from weibo db
    def is_wbimg_get_by_url(self, url):
        try:
            api.wbimg_get_by_url(url)
        except exception.WbimgUrlNotFound:
            return False
        return True

    # get url from weibo db
    def db_wbimg_get_by_url(self, url):
        return api.wbimg_get_by_url(url)

    # get mid from wbimg db
    def is_wbimg_get_by_mid(self, mid):
        try:
            api.wbimg_get_by_mid(mid)
        except exception.WbimgMidNotFound:
            return False
        return True

    # is exists wbimg by uid
    def is_wbimg_get_by_uid(self, uid):
        try:
            api.wbimg_get_by_uid(uid)
        except exception.WbimgUidNotFound:
            return False
        return True

    # get uid from wbimg db
    def db_wbimg_get_by_uid(self, uid):
        return api.wbimg_get_by_uid(uid)

    # get mid  and is_zf and pa_mid from wbimg db
    def db_wbimg_get_by_mid_and_zf(self, mid, is_zf=False):
        try:
            api.wbimg_get_by_mid_and_zf(mid)
        except exception.WbimgMidAndZfNotFound:
            return False
        return True

    # zfwbtext crate or update
    def db_zfwbtext_create_or_update(self, values):
        is_exist = self.is_zfwbtext_get_by_mid(values['mid'])
        if is_exist:
            self.db_zfwbtext_update(values)
        else:
            self.db_zfwbtext_create(values)

    # wbtext create
    def db_zfwbtext_create(self, values):
        return api.zfwbtext_create(values)

    # wbtext update
    def db_zfwbtext_update(self, values):
        return api.zfwbtext_update(values)

    # get mid from zfwbtext db
    def is_zfwbtext_get_by_mid(self, mid):
        try:
            api.zfwbtext_get_by_mid(mid)
        except exception.ZfwbtextMidNotFound:
            return False
        return True

    #  ----- option all zfwbimg start ----- #
    # zfwbimg crate or update
    def db_zfwbimg_create_or_update(self, values):
        is_exist = self.is_zfwbimg_get_by_url(values['url'])
        if is_exist:
            self.db_zfwbimg_update(values)
        else:
            self.db_zfwbimg_create(values)

    # zfwbimg create
    def db_zfwbimg_create(self, values):
        return api.zfwbimg_create(values)

    # wbimg update
    def db_zfwbimg_update(self, values):
        return api.zfwbimg_update(values)

    # get uid from zfwbimg db
    def is_zfwbimg_get_by_uid(self, uid):
        try:
            api.zfwbimg_get_by_uid(uid)
        except exception.ZfwbimgUidNotFound:
            return False
        return True

    # get uid from zfwbimg db
    def db_zfwbimg_get_by_uid(self, uid):
        return api.zfwbimg_get_by_uid(uid)

    # get mid from zfwbimg db
    def is_zfwbimg_get_by_mid(self, mid):
        try:
            api.zfwbimg_get_by_mid(mid)
        except exception.ZfwbimgMidNotFound:
            return False
        return True

    # get url from zfwbimg db by url
    def is_zfwbimg_get_by_url(self, url):
        try:
            api.zfwbimg_get_by_url(url)
        except exception.ZfwbimgUrlNotFound:
            return False
        return True

    #  ----- option all zfwbimg end ----- #
    # save all data to db
    def save_all_data(self):
        pass

db_api = Dbsave()
