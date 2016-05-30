# --*-- coding: utf-8 --*--

from sqlalchemy import *
from migrate import *

def _create_img_table(migrate_engine, drop=False):
    meta = MetaData(migrate_engine)
    meta.reflect(migrate_engine)

    # create img tables
    img = Table('img', meta,
                Column('created_at', DateTime),
                Column('updated_at', DateTime),
                Column('deleted_at', DateTime),
                Column('deleted', Boolean),

                Column('id', Integer, primary_key=True, nullable=False),
                # 微博mid
                Column('mid', BigInteger, nullable=False),

                # 用户UID
                Column('uid', BigInteger, nullable=False),

                # img所在地方
                Column('location', String(200), nullable=False),

                extend_existing=True,
                mysql_engine='InnoDB',
                mysql_charset='utf8')

    tables = [img]
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
    _create_img_table(migrate_engine, drop=False)


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    _create_img_table(migrate_engine, drop=True)
