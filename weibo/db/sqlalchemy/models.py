# --*-- coding: utf-8 --*--
"""
SQLAlchemy models for nova data.
"""

from sqlalchemy import Column, Integer, BigInteger, String, schema, VARCHAR
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, DateTime, Boolean, Text, Float
from sqlalchemy.orm import relationship, backref, object_mapper


from weibo.common import timeutils


BASE = declarative_base()

class WeiboBase(object):
    """Base class for Weibo Models."""

    __table_args__ = {'mysql_engine': 'InnoDB'}
    __table_initialized__ = False
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=timeutils.utcnow)
    updated_at = Column(DateTime, onupdate=timeutils.utcnow)
    deleted_at = Column(DateTime)
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
        self.deleted_at = timeutils.utcnow()
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
    gender = Column(String(15))

    # 等级
    urank = Column(Integer)

    # 阳光信用
    credit_score = Column(Integer)

    # 注册时间
    create_date = Column(String(150))

    # 记录删除时间

class Weibo(BASE, WeiboBase):
    __tablename__ = 'weibo'
    # 微博id
    mid = Column(BigInteger)

    # user id
    uid = Column(BigInteger)

    # text 文本信息
    text = Column(Text)

    # img 图片url 信息
    img = Column(String(64))

    # videos 视频 url 信息
    videos = Column(String(64))

    # 转发数量
    forward = Column(BigInteger)

    # 评论数量
    repeat = Column(BigInteger)

    # 点赞数量
    praised = Column(BigInteger)

    # 发布时间
    time_at = Column(String(150))


class Img(BASE, WeiboBase):
    __tablename__ = 'img'

    # 微博mid
    mid = Column(BigInteger, nullable=False)

    # 用户UID
    uid = Column(BigInteger, nullable=False)

    # img所在地方
    location = Column(String(200), nullable=False)
