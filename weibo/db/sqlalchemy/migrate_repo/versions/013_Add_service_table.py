from sqlalchemy import *
from migrate import *


def _create_services_table(migrate_engine, drop=False):
    meta = MetaData(migrate_engine)
    meta.reflect(migrate_engine)

    # create services tables
    services = Table('services', meta,
                     Column('created_time', DateTime),
                     Column('updated_time', DateTime),
                     Column('deleted_time', DateTime),
                     Column('deleted', Boolean),

                     # 主建
                     Column('id', BigInteger, primary_key=True, nullable=False),

                     # host name
                     Column('host', String(200)),

                     # binary
                     Column('binary', String(200)),

                     # binary
                     Column('topic', String(200)),

                     # report count 个数
                     Column('report_count', BigInteger),

                     # 是否取消
                     Column('disabled', Boolean),

                     # 取消的理由
                     Column('disabled_reason', VARCHAR(200)),

                     extend_existing=True,
                     mysql_engine='InnoDB',
                     mysql_charset='utf8')

    tables = [services]
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
    _create_services_table(migrate_engine, drop=False)


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    _create_services_table(migrate_engine, drop=True)
