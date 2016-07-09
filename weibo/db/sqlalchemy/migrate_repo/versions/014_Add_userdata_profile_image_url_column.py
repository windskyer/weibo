from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    meta = MetaData()
    meta.bind = migrate_engine

    # create column:

    userdata = Table('userdata', meta, autoload=True)
    profile_image_url = Column('profile_image_url', String(200))

    userdata.create_column(profile_image_url)


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta = MetaData()
    meta.bind = migrate_engine

    # create column:
    userdata = Table('userdata', meta, autoload=True)
    profile_image_url = Column('profile_image_url', String(200))

    userdata.drop_column(profile_image_url)
