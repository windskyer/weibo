# --*-- coding: utf-8 --*--
# Copyright (c) 2016
# author: zwei
# email: suifeng20@hotmail.com


import sys
import six

from weibo.common import log as logging

LOG = logging.getLogger(__name__)

class Error(Exception):
    """Base class for cfg exceptions."""

    def __init__(self, msg=None):
        self.msg = msg

    def __str__(self):
        return self.msg


class WeiboError(Exception):
    msg_fmt = ("An unknown exception occurred.")
    code = 500
    headers = {}
    safe = False

    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs
        if 'code' not in kwargs:
            try:
                self.kwargs['code'] = self.code
            except AttributeError:
                pass

        if not message:
            try:
                message = self.msg_fmt % kwargs
            except Exception:
                exc_info = sys.exc_info()
                LOG.exception('Exception in string format operation')
                for name, value in six.iteritems(kwargs):
                    LOG.error("%s: %s" % (name, value))
                six.reraise(*exc_info)

        self.message = message
        super(WeiboError, self).__init__(message)


class LogConfigError(WeiboError):
    msg_fmt = "Not Found %(binfile)s configfile"


class NoSuchOptError(WeiboError):
    msg_fmt = "'module' object has no attribute %(key)s"


class ConfigFileParseError(Error):
    """Raised if there is an error parsing a config file."""

    def __init__(self, config_file, msg):
        self.config_file = config_file
        self.msg = msg

    def __str__(self):
        return 'Failed to parse %s: %s' % (self.config_file, self.msg)

# db exception
class WeiboMidExists(WeiboError):
    msg_fmt = ("Weibo %(mid)s is exists.")

class WeiboMidNotFound(WeiboError):
    msg_fmt = ("Weibo %(mid)s could not be found.")

class WeiboIdNotFound(WeiboError):
    msg_fmt = ("Weibo %(id)s could not be found.")

class WeiboUidNotFound(WeiboError):
    msg_fmt = ("Weibo %(uid)s could not be found.")


class WbtextMidExists(WeiboError):
    msg_fmt = ("Wbtext %(mid)s is exists.")

class ZfwbtextMidExists(WeiboError):
    msg_fmt = ("zfwbtext %(mid)s is exists.")

class WbtextMidNotFound(WeiboError):
    msg_fmt = ("Wbtext %(mid)s could not be found.")

class ZfwbtextMidNotFound(WeiboError):
    msg_fmt = ("zfwbtext %(mid)s could not be found.")

class WbtextIdNotFound(WeiboError):
    msg_fmt = ("Wbtext %(id)s could not be found.")


class WbtextUidNotFound(WeiboError):
    msg_fmt = ("Wbtext %(uid)s could not be found.")

class WbimgUrlNotFound(WeiboError):
    msg_fmt = ("Wbimg %(url)s could not be found.")

class ZfwbimgUrlNotFound(WeiboError):
    msg_fmt = ("Zfwbimg %(url)s could not be found.")

class WbimgUrlExists(WeiboError):
    msg_fmt = ("Wbimg %(url)s is exists.")

class ZfwbimgUrlExists(WeiboError):
    msg_fmt = ("Zfwbimg %(url)s is exists.")

class WbimgMidExists(WeiboError):
    msg_fmt = ("Wbimg %(mid)s is exists.")

class WbimgMidNotFound(WeiboError):
    msg_fmt = ("Wbimg %(mid)s could not be found.")

class ZfwbimgMidNotFound(WeiboError):
    msg_fmt = ("zfwbimg %(mid)s could not be found.")

class WbimgIdNotFound(WeiboError):
    msg_fmt = ("Wbimg %(id)s could not be found.")

class WbimgUidNotFound(WeiboError):
    msg_fmt = ("Wbimg %(uid)s could not be found.")


class UserdataMidNotFound(WeiboError):
    msg_fmt = ("Userdata mid %(mid)s not found exists.")

class UserdataNameExists(WeiboError):
    msg_fmt = ("Userdata '%(userdata_name)s' user already exists.")


class UserdataUidNotFound(WeiboError):
    msg_fmt = ("Userdata uid %(uid)s not found exists.")


class UserdataIdNotFound(WeiboError):
    msg_fmt = ("Userdata id %(id)s not found exists.")


class UserdataNameNotFound(WeiboError):
    msg_fmt = ("Userdata  name %(screen_name)s not found exists.")


class NotFoundChildrenTag(WeiboError):
    msg_fmt = ("Not Found %(name)s attrs %(class)s, "
               "%(nova-type)s children tag ")


class DetailNotFound(WeiboError):
    msg_fmt = ("Not Found weibo detail info")


class NicknameNotNull(WeiboError):
    msg_fmt = ("nickname is Not null")

class NotFoundImg(WeiboError):
    msg_fmt = ("Not download %(url)s img to local disk")

class ZfwbimgUidNotFound(WeiboError):
    msg_fmt = ("ZfWbimg %(uid)s could not be found.")

class NotFound(WeiboError):
    msg_fmt = ("ZfWbimg %(uid)s could not be found.")

