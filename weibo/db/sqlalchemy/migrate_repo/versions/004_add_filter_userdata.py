from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    # add column:
    userdata = Table('userdata', meta, autoload=True)
    profile_url = Column('profile_url', String(150))

    userdata.create_column(profile_url)

def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine
    userdata = Table('userdata', meta, autoload=True)
    profile_url = Column('profile_url', String(150))
    userdata.drop_column(profile_url)
