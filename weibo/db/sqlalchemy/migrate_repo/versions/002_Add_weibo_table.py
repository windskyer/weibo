# --*-- coding: utf-8 --*--

from sqlalchemy import *
from migrate import *


def _create_weibo_table(migrate_engine, drop=False):
    meta = MetaData(migrate_engine)
    meta.reflect(migrate_engine)

    # create weibo tables
    weibo = Table('weibo', meta,
                  Column('created_time', DateTime),
                  Column('updated_time', DateTime),
                  Column('deleted_time', DateTime),
                  Column('deleted', Boolean),

                  # 主建
                  Column('id', BigInteger, primary_key=True, nullable=False),

                  # 微博id
                  Column('mid', BigInteger, nullable=False),

                  # user id
                  Column('uid', BigInteger, nullable=False),

                  # text 文本信息
                  Column('text', Text, nullable=False),

                  # img 图片url 信息
                  Column('img', VARCHAR(250), nullable=False),

                  # videos 视频 url 信息
                  Column('videos', VARCHAR(250), nullable=False),

                  # 转发数量
                  Column('forward', BigInteger, nullable=False),

                  # 评论数量
                  Column('repeat', BigInteger, nullable=False),

                  # 点赞数量
                  Column('praised', BigInteger, nullable=False),

                  # 发布时间
                  Column('time_at', VARCHAR(150), nullable=True),

                  extend_existing=True,
                  mysql_engine='InnoDB',
                  mysql_charset='utf8')

    tables = [weibo]
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
    _create_weibo_table(migrate_engine, drop=False)


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    _create_weibo_table(migrate_engine, drop=True)
