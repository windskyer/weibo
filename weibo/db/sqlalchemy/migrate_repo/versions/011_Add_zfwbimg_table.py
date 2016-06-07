# coding:utf-8
from sqlalchemy import *
from migrate import *

def _create_zfwbimg_table(migrate_engine, drop=False):
    meta = MetaData(migrate_engine)
    meta.reflect(migrate_engine)

    # create zfwbimg tables
    zfwbimg = Table('zfwbimg', meta,
                    Column('created_time', DateTime),
                    Column('updated_time', DateTime),
                    Column('deleted_time', DateTime),
                    Column('deleted', Boolean),

                    # 主建
                    Column('id', BigInteger, primary_key=True, nullable=False),

                    # 微博mid
                    Column('mid', BigInteger, nullable=False),

                    # 用户 id
                    Column('uid', BigInteger, nullable=False),

                    # img所在地方
                    Column('location', String(200)),

                    Column('url', VARCHAR(200)),
                    Column('is_zf', Boolean),
                    Column('pa_mid', BigInteger),

                    extend_existing=True,
                    mysql_engine='InnoDB',
                    mysql_charset='utf8')

    tables = [zfwbimg]
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
    _create_zfwbimg_table(migrate_engine, drop=False)


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    _create_zfwbimg_table(migrate_engine, drop=True)
