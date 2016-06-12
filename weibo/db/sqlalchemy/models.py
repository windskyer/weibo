# --*-- coding: utf-8 --*--
"""
SQLAlchemy models for nova data.
"""

from sqlalchemy import Column, Integer, BigInteger, String, schema, VARCHAR
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, DateTime, Boolean, Text, Float
from sqlalchemy.orm import relationship, backref, object_mapper


from weibo.db.sqlalchemy import session
from weibo.common import timeutils

get_session = session.get_session

BASE = declarative_base()

class WeiboBase(object):
    """Base class for Weibo Models."""

    __table_args__ = {'mysql_engine': 'InnoDB'}
    __table_initialized__ = False
    id = Column(BigInteger, primary_key=True, nullable=False)
    created_time = Column(DateTime, default=timeutils.utcnow)
    updated_time = Column(DateTime, onupdate=timeutils.utcnow)
    deleted_time = Column(DateTime)
    deleted = Column(Boolean, default=False)
    metadata = None


    def save(self, session=None):
        """Save this object."""
        if not session:
            session = get_session()

        session.add(self)
        try:
            session.flush()
        except IntegrityError, e:
            if str(e).endswith('is not unique'):
                raise exception.Duplicate(str(e))
            else:
                raise

    def delete(self, session=None):
        """Delete this object."""
        self.deleted = True
        self.deleted_time = timeutils.utcnow()
        self.save(session=session)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def get(self, key, default=None):
        return getattr(self, key, default)

    def __iter__(self):
        columns = dict(object_mapper(self).columns).keys()
        # NOTE(russellb): Allow models to specify other keys that can be looked
        # up, beyond the actual db columns.  An example would be the 'name'
        # property for an Instance.
        if hasattr(self, '_extra_keys'):
            columns.extend(self._extra_keys())
            self._i = iter(columns)
            return self

    def next(self):
        n = self._i.next()
        return n, getattr(self, n)

    def update(self, values):
        """Make the model object behave like a dict"""
        for k, v in values.iteritems():
            setattr(self, k, v)

    def iteritems(self):
        """Make the model object behave like a dict.

        Includes attributes from joins."""
        local = dict(self)
        joined = dict([(k, v) for k, v in self.__dict__.iteritems()
                       if not k[0] == '_'])
        local.update(joined)
        return local.iteritems()


class Userdata(BASE, WeiboBase):
    __tablename__ = 'userdata'

    # 用户id
    uid = Column(BigInteger)

    # 昵称
    screen_name = Column(String(64))

    # 友好名称
    name = Column(String(32))

    # 用户所在地方
    location = Column(String(64))

    # 简介
    description = Column(String(200))

    # 关注数量
    friends_count = Column(BigInteger)

    # 粉丝数量
    followers_count = Column(BigInteger)

    # 标签
    ability_tags =  Column(String(15))

    # 性别
    gender = Column(String(15), default='m')

    # 等级
    urank = Column(Integer, default=0)

    # 阳光信用
    credit_score = Column(Integer, default=0)

    # 注册时间
    created_at = Column(String(150))

    # 主页地址
    profile_url = Column(String(150))

class Weibo(BASE, WeiboBase):
    __tablename__ = 'weibo'
    # 微博id
    mid = Column(BigInteger, nullable=False)

    # user id
    uid = Column(BigInteger, nullable=False)

    # text 文本信息
    # text = Column(Text)

    # img 图片url 信息
    # img = Column(String(250))

    # videos 视频 url 信息
    # videos = Column(String(250))

    # 转发数量
    forward = Column(BigInteger)

    # 评论数量
    repeat = Column(BigInteger)

    # 点赞数量
    praised = Column(BigInteger)

    # 发布时间
    time_at = Column(String(150))

class Zfwbimg(BASE, WeiboBase):
    __tablename__ = 'zfwbimg'

    # 微博mid
    mid = Column(BigInteger, nullable=False)

    # 用户UID
    uid = Column(BigInteger, nullable=False)

    # img所在地方
    location = Column(String(200))

    # img 的 url 地址
    url = Column(String(200))

    # 是否是转发微博
    is_zf = Column(Boolean, default=False)

    # 转发微博的mid
    pa_mid = Column(BigInteger, nullable=True)


class Wbimg(BASE, WeiboBase):
    __tablename__ = 'wbimg'

    # 微博mid
    mid = Column(BigInteger, nullable=False)

    # 用户UID
    uid = Column(BigInteger, nullable=False)

    # img所在地方
    location = Column(String(200))

    # img 的 url 地址
    url = Column(String(200))

    # 是否是转发微博
    is_zf = Column(Boolean, default=False)

    # 被转发weibo 的mid
    zf_mid = Column(BigInteger, nullable=True)


class Wbtext(BASE, WeiboBase):
    __tablename__ = 'wbtext'

    # 微博mid
    mid = Column(BigInteger, nullable=False)

    # 用户UID
    uid = Column(BigInteger, nullable=False)

    # text info
    text = Column(Text)

    # face 表情 info
    face = Column(Text)

    # 文本中的link 的 url 地址
    url = Column(Text)

    # 是否是转发微博
    is_zf = Column(Boolean, default=False)

    # 转发weibo 的mid
    zf_mid = Column(BigInteger, nullable=True)


class Zfwbtext(BASE, WeiboBase):
    __tablename__ = 'zfwbtext'

    # 微博mid
    mid = Column(BigInteger, nullable=False)

    # 用户UID
    uid = Column(BigInteger, nullable=False)

    # text info
    text = Column(Text)

    # face 表情 info
    face = Column(Text)

    # 文本中的link 的 url 地址
    url = Column(Text)

    # 是否是转发微博
    is_zf = Column(Boolean, default=False)

    # 被转发weibo 的mid
    pa_mid = Column(BigInteger, nullable=True)
