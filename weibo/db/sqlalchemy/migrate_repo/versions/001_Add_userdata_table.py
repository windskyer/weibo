# --*-- coding:utf-8 --*--

from sqlalchemy import *
from migrate import *


def _create_userdata_table(migrate_engine, drop=False):
    meta = MetaData(migrate_engine)
    meta.reflect(migrate_engine)

    # create userdata tables
    userdata = Table('userdata', meta,
                     Column('created_time', DateTime),
                     Column('updated_time', DateTime),
                     Column('deleted_time', DateTime),
                     Column('deleted', Boolean),

                     # 主建
                     Column('id', BigInteger, primary_key=True, nullable=False),

                     # 用户UID
                     Column('uid', BigInteger, nullable=False),

                     # 昵称
                     Column('screen_name', VARCHAR(64), nullable=False),

                     # 友好名称
                     Column('name', VARCHAR(32), nullable=True),

                     # 用户所在地方
                     Column('location', VARCHAR(64), nullable=True),

                     # 简介
                     Column('description', VARCHAR(200), nullable=True),

                     # 关注数量
                     Column('friends_count', BigInteger, nullable=False),

                     # 粉丝数量
                     Column('followers_count', BigInteger, nullable=True),

                     # 标签
                     Column('ability_tags', VARCHAR(15), nullable=True),

                     # 性别
                     Column('gender', VARCHAR(15), nullable=True),

                     # 等级
                     Column('urank', Integer, nullable=True),

                     # 阳光信用
                     Column('credit_score', Integer, nullable=True),

                     # 注册时间
                     Column('created_at', String(150), nullable=True),

                     # homepage 主页
                     Column('homepage', String(150), nullable=True),

                     extend_existing=True,
                     mysql_engine='InnoDB',
                     mysql_charset='utf8')

    tables = [userdata]
    for table in tables:
        if not drop:
            try:
                table.create()
            except Exception:
                raise
        else:
            try:
                table.drop()
            except Exception:
                raise


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    _create_userdata_table(migrate_engine, False)


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    _create_userdata_table(migrate_engine, True)
