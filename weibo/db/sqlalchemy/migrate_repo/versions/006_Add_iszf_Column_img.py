from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    meta = MetaData()
    meta.bind = migrate_engine

    # delete column:
    wbimg = Table('wbimg', meta, autoload=True)
    url = Column('url', VARCHAR(200))
    is_zf = Column('is_zf', Boolean)
    wbimg.create_column(url)
    wbimg.create_column(is_zf)



def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta = MetaData()
    meta.bind = migrate_engine

    # delete column:
    wbimg = Table('wbimg', meta, autoload=True)
    url = Column('url', VARCHAR(200))
    is_zf = Column('is_zf', Boolean)
    wbimg.drop_column(url)
    wbimg.drop_column(is_zf)
