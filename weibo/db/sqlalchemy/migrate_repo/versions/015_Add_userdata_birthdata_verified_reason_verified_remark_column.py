from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    meta = MetaData()
    meta.bind = migrate_engine

    # create column:

    userdata = Table('userdata', meta, autoload=True)
    birthdate = Column('birthdate', String(200))
    verified_reason = Column('verified_reason', String(200))
    verified = Column('verified', Boolean, default=False)
    remark = Column('remark', String(200))

    userdata.create_column(birthdate)
    userdata.create_column(verified_reason)
    userdata.create_column(verified)
    userdata.create_column(remark)


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta = MetaData()
    meta.bind = migrate_engine

    # create column:
    userdata = Table('userdata', meta, autoload=True)
    birthdate = Column('birthdate', String(200))
    verified_reason = Column('verified_reason', String(200))
    verified = Column('verified', Boolean)
    remark = Column('remark', String(200))

    userdata.drop_column(birthdate)
    userdata.drop_column(verified_reason)
    userdata.drop_column(verified)
    userdata.drop_column(remark)
