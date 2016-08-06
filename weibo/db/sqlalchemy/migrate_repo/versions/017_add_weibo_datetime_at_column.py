from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    meta = MetaData()
    meta.bind = migrate_engine

    # create column:

    weibo = Table('weibo', meta, autoload=True)
    datetime_at = Column('datetime_at', DateTime)

    weibo.create_column(datetime_at)


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta = MetaData()
    meta.bind = migrate_engine

    # create column:
    weibo = Table('weibo', meta, autoload=True)
    datetime_at = Column('datetime_at', DateTime)

    weibo.drop_column(datetime_at)
