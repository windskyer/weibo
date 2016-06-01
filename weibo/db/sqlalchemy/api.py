# -*- coding: utf-8 -*-
# author: zwei
# email: suifeng20@hotmail.com


from weibo import db
from weibo import exception
from weibo.db.sqlalchemy import models
from weibo.db.sqlalchemy.session import get_session

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


def _get_query(model_class, id_field=None, id=None,
                        session=None, read_deleted=None):
    query = model_query(model_class, session=session,
                        read_deleted=read_deleted)

    if id and id_field:
        query = query.filter(id_field == id)

    return query


def userdata_create(values):
    session = get_session()
    userdata = _get_query(models.Userdata,
                                   models.Userdata.uid,
                                   values['uid'],
                                   session=session,
                                   read_deleted='no').first()
    if not userdata:
        userdata = models.Userdata()
        userdata.update(values)
        userdata.save(session=session)
    else:
        raise exception.UserdataNameExists(userdata_name=values['name'])

    return userdata_get_by_uid(userdata.uid)


def userdata_update(values, session=None):
    if not session:
        session = get_session()
    uid = values.pop('uid')
    with session.begin():
        userdata = userdata_get_by_uid(uid, session=session)
        userdata.update(values)
        userdata.save(session=session)

    return userdata_get_by_uid(uid)


def userdata_get_all(session=None):
    if not session:
        session = get_session()
    result = model_query(models.Userdata, session=session)
    return result.all()


def userdata_delete(id):
    session = get_session()
    userdata = userdata_get_by_id(id)
    if userdata:
        userdata.delete()


def userdata_delete_uid(uid):
    session = get_session()
    userdata = userdata_get_by_uid(uid)
    if userdata:
        userdata.delete()


def userdata_delete_name(name):
    session = get_session()
    userdata = userdata_get_by_name(name)
    if userdata:
        userdata.delete()


def userdata_get_by_name(name, session=None):
    result = model_query(models.Userdata, session=session).\
            filter_by(name=name).\
            first()
    if not result:
        raise exception.UserdataNameNotFound(name=name)

    return result


def userdata_get_by_id(id, session=None):
    result = model_query(models.Userdata, session=session).\
                     filter_by(id=id).\
                     first()
    if not result:
        raise exception.UserdataIdNotFound(id=id)

    return result


def userdata_get_by_uid(uid, session=None):
    result = model_query(models.Userdata, session=session).\
                     filter_by(uid=uid).\
                     first()
    if not result:
        raise exception.UserdataUidNotFound(uid=uid)

    return result


def weibo_create(values, session=None):
    if not session:
        session = get_session()

    weibo = _get_query(models.Weibo,
                       models.Weibo.mid,
                       values['mid'],
                       session=session,
                       read_deleted='no').first()

    if not weibo:
        weibo = models.Weibo()
        weibo.update(values)
        weibo.save(session=session)
    else:
        raise exception.WeiboMidExists(mid=mid)

    return weibo_get_by_mid(weibo.mid)


def weibo_update(values, session=None):
    if not session:
        session = get_session()
    mid = values.pop('mid')
    with session.begin():
        weibo = weibo_get_by_mid(mid, session=session)
        weibo.update(values)
        weibo.save(session=session)

    return weibo_get_by_mid(mid)


def weibo_delete(id, session=None):
    if not session:
        session = get_session()

    weibo = weibo_get_by_id(id)
    if weibo:
        weibo.delete()


def weibo_delete_mid(mid, session=None):
    if not session:
        session = get_session()

    weibo = weibo_get_by_mid(mid)
    if weibo:
        weibo.delete()


def weibo_delete_uid(uid, session=None):
    if not session:
        session = get_session()

    weibos = weibo_get_by_uid(uid)
    if weibo in weibos:
        weibo.delete()


def weibo_get_by_id(id, session=None):
    result = model_query(models.Weibo, session=session).\
                     filter_by(id=id).\
                     first()
    if not result:
        raise exception.UserdataMidNotFound(mid=mid)

    return result


def weibo_get_by_mid(mid, session=None):
    result = model_query(models.Weibo, session=session).\
                     filter_by(mid=mid).\
                     first()
    if not result:
        raise exception.UserdataMidNotFound(mid=mid)

    return result


def weibo_get_by_uid(uid, session=None):
    result = model_query(models.Weibo, session=session).\
                     filter_by(uid=uid).\
                     all()
    if not result:
        raise exception.UserdataMidNotFound(mid=mid)

    return result


def weibo_get_all(session=None):
    result = model_query(models.Weibo, session=session).\
                     all()
    return result


if __name__ == '__main__':
    CONF('weibo.conf')
    values = {u'uid': 1337970873, u'screen_name': u'\u6d77\u6d9b\u6cd5\u5e08', u'name': u'\u6d77\u6d9b\u6cd5\u5e08', u'location': u'\u53f0\u6e7e',
     u'description': u'雷东', u'friends_count': 1378,  u'followers_count': 46336090, 'ability_tags' : 'unknow', u'gender': u'm', u'urank': 27,  u'credit_score': 80,
     u'created_at': u'Wed Mar 30 17:02:40 +0800 2011',}
    #userdata_delete_uid(values['uid'])
    #userdata_delete(2)
    #try:
    #    userdata_create(values)
    #except exception.UserdataNameExists as e:
    #    print(e.message)
    #userdata_get_by_uid(values['uid'])
    #userdata_get_all()
    #userdata_get_by_name('海涛法师')
    #userdata_update(values)
    print(len(userdata_get_all()))
