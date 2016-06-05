from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    meta = MetaData()
    meta.bind = migrate_engine

    # delete column:
    userdata = Table('weibo', meta, autoload=True)
    text = Column('text', Text)
    img = Column('img', VARCHAR(250), nullable=False)
    videos = Column('videos', VARCHAR(250), nullable=False)
    userdata.drop_column(text)
    userdata.drop_column(img)
    userdata.drop_column(videos)


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta = MetaData()
    meta.bind = migrate_engine

    # add column:
    userdata = Table('weibo', meta, autoload=True)
    text = Column('text', Text)
    img = Column('img', VARCHAR(250), nullable=False)
    videos = Column('videos', VARCHAR(250), nullable=False)
    userdata.create_column(text)
    userdata.create_column(img)
    userdata.create_column(videos)
