# -*- coding: utf-8 -*-
#author: zwei


from weibo import db
from weibo.db.sqlalchemy import models
from weibo.db.sqlalchemy.session import get_session
from weibo import exception

from weibo.common import cfg
from weibo.common import log as logging

CONF = cfg.CONF
LOG = logging.getLogger(__name__)



def model_query(model, *args, **kwargs):
    """Query helper that accounts for context's `read_deleted` field.

    :param session: if present, the session to use
    :param read_deleted: if present, overrides context's read_deleted field.
    :param project_only: if present and context is user-type, then restrict
            query to match the context's project_id. If set to 'allow_none',
            restriction includes project_id = None.
    """
    read_deleted = kwargs.get('read_deleted', 'no')
    session = kwargs.get('session') or get_session()

    query = session.query(model, *args)

    if read_deleted == 'no':
        query = query.filter_by(deleted=False)
    elif read_deleted == 'yes':
        pass  # omit the filter to include deleted and active
    elif read_deleted == 'only':
        query = query.filter_by(deleted=True)
    else:
        raise Exception(
                _("Unrecognized read_deleted value '%s'") % read_deleted)

    return query

def userdata_create(values, metadata=None):
    session = get_session()
    userdata = _aggregate_get_query(context,
                                    models.Aggregate,
                                    models.Aggregate.name,
                                    values['name'],
                                    session=session,
                                    read_deleted='no').first()
    if not aggregate:
        aggregate = models.Aggregate()
        aggregate.update(values)
        aggregate.save(session=session)
    else:
        raise exception.AggregateNameExists(aggregate_name=values['name'])
    if metadata:
        aggregate_metadata_add(context, aggregate.id, metadata)
    return aggregate_get(context, aggregate.id)

@require_admin_context
def aggregate_get(context, aggregate_id):
    aggregate = _aggregate_get_query(context,
                                     models.Aggregate,
                                     models.Aggregate.id,
                                     aggregate_id).first()

    if not aggregate:
        raise exception.AggregateNotFound(aggregate_id=aggregate_id)

    return aggregate


def userdata_get_by_id(id, session=None):
    result = model_query(models.Userdata, session=session).\
                     filter_by(id=id).\
                     first()
    if not result:
        raise exception.UserdataNotFound(id=id)

    return result


def userdata_get_by_uid(uid, session=None):
    result = model_query(models.Userdata, session=session).\
                     filter_by(uid=uid).\
                     first()
    if not result:
        raise exception.UserdataNotFound(uid=uid)

    return result

if __name__ == '__main__':
    CONF('weibo.conf')
    print CONF.database
    userdata_get_by_id(1)
