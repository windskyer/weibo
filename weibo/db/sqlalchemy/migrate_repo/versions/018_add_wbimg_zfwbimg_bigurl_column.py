from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    meta = MetaData()
    meta.bind = migrate_engine

    # create column:

    wbimg = Table('wbimg', meta, autoload=True)
    zfwbimg = Table('zfwbimg', meta, autoload=True)
    bigurl = Column('bigurl', String(200))

    wbimg.create_column(bigurl)

    bigurl = Column('bigurl', String(200))
    zfwbimg.create_column(bigurl)


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta = MetaData()
    meta.bind = migrate_engine

    wbimg = Table('wbimg', meta, autoload=True)
    zfwbimg = Table('zfwbimg', meta, autoload=True)

    bigurl = Column('bigurl', String(200))
    wbimg.drop_column(bigurl)

    bigurl = Column('bigurl', String(200))
    zfwbimg.drop_column(bigurl)
