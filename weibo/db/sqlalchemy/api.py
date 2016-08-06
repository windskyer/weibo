# -*- coding: utf-8 -*-
# author: zwei
# email: suifeng20@hotmail.com


from weibo import exception
from weibo.db.sqlalchemy import models
from weibo.db.sqlalchemy.session import get_session

from weibo.common import cfg
from weibo.common import timeutils
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
    userdata = userdata_get_by_id(id, session)
    if userdata:
        userdata.delete(session)


def userdata_delete_uid(uid):
    session = get_session()
    userdata = userdata_get_by_uid(uid, session)
    if userdata:
        userdata.delete(session)


def userdata_delete_name(name):
    session = get_session()
    userdata = userdata_get_by_name(name, session)
    if userdata:
        userdata.delete(session)


def userdata_get_by_name(name, session=None):
    result = model_query(models.Userdata, session=session).\
        filter_by(screen_name=name).\
        first()
    if not result:
        raise exception.UserdataNameNotFound(screen_name=name)
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


# ----all options weibo -----#
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
        raise exception.WeiboMidExists(mid=values['mid'])

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
    for weibo in weibos:
        weibo.delete()


def weibo_get_by_id(id, session=None):
    result = model_query(models.Weibo, session=session).\
                     filter_by(id=id).\
                     first()
    if not result:
        raise exception.WeiboIdNotFound(id=id)

    return result


def weibo_get_by_mid(mid, session=None):
    result = model_query(models.Weibo, session=session).\
                     filter_by(mid=mid).\
                     first()
    if not result:
        raise exception.WeiboMidNotFound(mid=mid)

    return result


def weibo_get_by_uid(uid, session=None):
    result = model_query(models.Weibo, session=session).\
                     filter_by(uid=uid).\
                     all()
    if not result:
        raise exception.WeiboUidNotFound(uid=uid)

    return result


def weibo_get_all(session=None):
    result = model_query(models.Weibo, session=session).\
                     all()
    return result


# wbtext table options
def wbtext_create(values, session=None):
    if not session:
        session = get_session()

    wbtext = _get_query(models.Wbtext,
                        models.Wbtext.mid,
                        values['mid'],
                        session=session,
                        read_deleted='no').first()

    if not wbtext:
        wbtext = models.Wbtext()
        wbtext.update(values)
        wbtext.save(session=session)
    else:
        raise exception.WbtextMidExists(mid=values['mid'])

    return wbtext_get_by_mid(wbtext.mid)


def wbtext_update(values, session=None):
    if not session:
        session = get_session()
    mid = values.pop('mid')
    with session.begin():
        wbtext = wbtext_get_by_mid(mid, session=session)
        wbtext.update(values)
        wbtext.save(session=session)

    return wbtext_get_by_mid(mid)


def wbtext_delete(id, session=None):
    if not session:
        session = get_session()

    wbtext = wbtext_get_by_id(id)
    if wbtext:
        wbtext.delete()


def wbtext_delete_mid(mid, session=None):
    if not session:
        session = get_session()

    wbtext = wbtext_get_by_mid(mid)
    if wbtext:
        wbtext.delete()


def wbtext_delete_uid(uid, session=None):
    if not session:
        session = get_session()

    wbtexts = wbtext_get_by_uid(uid)
    for wbtext in wbtexts:
        wbtext.delete()


def wbtext_get_by_id(id, session=None):
    result = model_query(models.Wbtext, session=session).\
                     filter_by(id=id).\
                     first()
    if not result:
        raise exception.WbtextIdNotFound(id=id)

    return result


def wbtext_get_by_mid(mid, session=None):
    result = model_query(models.Wbtext, session=session).\
                     filter_by(mid=mid).\
                     first()
    if not result:
        raise exception.WbtextMidNotFound(mid=mid)

    return result


def wbtext_get_by_uid(uid, session=None):
    result = model_query(models.Wbtext, session=session).\
                     filter_by(uid=uid).\
                     all()
    if not result:
        raise exception.WbtextUidNotFound(uid=uid)

    return result


def wbtext_get_by_mid_and_zf(mid, is_zf=False, session=None):
    result = model_query(models.Wbtext, session=session).\
                     filter_by(mid=mid).\
                     filter_by(is_zf=is_zf).\
                     first()

    if not result:
        raise exception.WbtextMidAndZfNotFound(mid=mid,
                                               is_zf=is_zf)

    return result


# wbimg table options
def wbimg_create(values, session=None):
    if not session:
        session = get_session()

    url = values['url']
    wbimg = _get_query(models.Wbimg,
                       models.Wbimg.url,
                       url,
                       session=session,
                       read_deleted='no').first()

    if not wbimg:
        wbimg = models.Wbimg()
        wbimg.update(values)
        wbimg.save(session=session)
    else:
        raise exception.WbimgUrlExists(url=url)

    return wbimg_get_by_url(wbimg.url)


def wbimg_update(values, session=None):
    if not session:
        session = get_session()
    url = values.get('url')
    with session.begin():
        wbimg = wbimg_get_by_url(url, session=session)
        wbimg.update(values)
        wbimg.save(session=session)

    return wbimg_get_by_url(url)


def wbimg_delete(id, session=None):
    if not session:
        session = get_session()

    wbimg = wbimg_get_by_id(id)
    if wbimg:
        wbimg.delete()


def wbimg_delete_mid(mid, session=None):
    if not session:
        session = get_session()

    wbimg = wbimg_get_by_mid(mid)
    if wbimg:
        wbimg.delete()


def wbimg_delete_uid(uid, session=None):
    if not session:
        session = get_session()

    wbimgs = wbimg_get_by_uid(uid)
    for wbimg in wbimgs:
        wbimg.delete()


def wbimg_get_by_url(url, session=None):
    result = model_query(models.Wbimg, session=session).\
                     filter_by(url=url).\
                     first()
    if not result:
        raise exception.WbimgUrlNotFound(url=url)

    return result


def wbimg_get_by_id(id, session=None):
    result = model_query(models.Wbimg, session=session).\
                     filter_by(id=id).\
                     first()
    if not result:
        raise exception.WbimgIdNotFound(id=id)

    return result


def wbimg_get_by_mid_and_zf(mid, is_zf=False, session=None):
    result = model_query(models.Wbimg, session=session).\
                     filter_by(mid=mid).\
                     filter_by(is_zf=is_zf).\
                     first()
    if not result:
        raise exception.WbimgMidAndZfNotFound(mid=mid,
                                              is_zf=is_zf)

    return result


def wbimg_get_by_uid(uid, session=None):
    result = model_query(models.Wbimg, session=session).\
                     filter_by(uid=uid).\
                     all()
    if not result:
        raise exception.WbimgUidNotFound(uid=uid)

    return result


def wbimg_get_by_uid_location(uid, session=None):
    result = model_query(models.Wbimg, session=session).\
                     filter_by(uid=uid).\
                     filter_by(location=None).\
                     all()
    return result


def wbimg_get_by_mid(mid, session=None):
    result = model_query(models.Wbimg, session=session).\
                     filter_by(mid=mid).\
                     all()
    if not result:
        raise exception.WbimgMidNotFound(mid=mid)

    return result


# zfwbimg table options
def zfwbimg_create(values, session=None):
    if not session:
        session = get_session()

    url = values['url']
    zfwbimg = _get_query(models.Zfwbimg,
                         models.Zfwbimg.url,
                         url,
                         session=session,
                         read_deleted='no').first()

    if not zfwbimg:
        zfwbimg = models.Zfwbimg()
        zfwbimg.update(values)
        zfwbimg.save(session=session)
    else:
        raise exception.ZfwbimgUrlExists(url=url)

    return zfwbimg_get_by_url(zfwbimg.url)


def zfwbimg_update(values, session=None):
    if not session:
        session = get_session()
    url = values.get('url')
    with session.begin():
        zfwbimg = zfwbimg_get_by_url(url, session=session)
        zfwbimg.update(values)
        zfwbimg.save(session=session)

    return zfwbimg_get_by_url(url)


def zfwbimg_delete(id, session=None):
    if not session:
        session = get_session()

    zfwbimg = zfwbimg_get_by_id(id)
    if zfwbimg:
        zfwbimg.delete()


def zfwbimg_delete_mid(mid, session=None):
    if not session:
        session = get_session()

    zfwbimgs = zfwbimg_get_by_mid(mid)
    for zfwbimg in zfwbimgs:
        zfwbimg.delete()


def zfwbimg_delete_uid(uid, session=None):
    if not session:
        session = get_session()

    zfwbimgs = zfwbimg_get_by_uid(uid)
    for zfwbimg in zfwbimgs:
        zfwbimg.delete()


def zfwbimg_get_by_url(url, session=None):
    result = model_query(models.Zfwbimg, session=session).\
                     filter_by(url=url).\
                     first()
    if not result:
        raise exception.ZfwbimgUrlNotFound(url=url)

    return result


def zfwbimg_get_by_id(id, session=None):
    result = model_query(models.Zfwbimg, session=session).\
                     filter_by(id=id).\
                     first()
    if not result:
        raise exception.ZfwbimgIdNotFound(id=id)

    return result


def zfwbimg_get_by_mid_and_zf(mid, is_zf=False, session=None):
    result = model_query(models.Zfwbimg, session=session).\
                     filter_by(mid=mid).\
                     filter_by(is_zf=is_zf).\
                     first()
    if not result:
        raise exception.ZfwbimgMidAndZfNotFound(mid=mid,
                                                is_zf=is_zf)

    return result


def zfwbimg_get_by_uid(uid, session=None):
    result = model_query(models.Zfwbimg, session=session).\
                     filter_by(uid=uid).\
                     all()
    if not result:
        raise exception.ZfwbimgUidNotFound(uid=uid)

    return result


def zfwbimg_get_by_uid_location(uid, session=None):
    result = model_query(models.Zfwbimg, session=session).\
                     filter_by(uid=uid).\
                     filter_by(location=None).\
                     all()
    return result


def zfwbimg_get_by_mid(mid, session=None):
    result = model_query(models.Zfwbimg, session=session).\
                     filter_by(mid=mid).\
                     all()
    if not result:
        raise exception.ZfwbimgMidNotFound(mid=mid)

    return result


# zfwbtext table options
def zfwbtext_create(values, session=None):
    if not session:
        session = get_session()

    zfwbtext = _get_query(models.Zfwbtext,
                          models.Zfwbtext.mid,
                          values['mid'],
                          session=session,
                          read_deleted='no').first()

    if not zfwbtext:
        zfwbtext = models.Zfwbtext()
        zfwbtext.update(values)
        zfwbtext.save(session=session)
    else:
        raise exception.ZfwbtextMidExists(mid=values['mid'])

    return zfwbtext_get_by_mid(zfwbtext.mid)


def zfwbtext_update(values, session=None):
    if not session:
        session = get_session()
    mid = values.pop('mid')
    with session.begin():
        zfwbtext = zfwbtext_get_by_mid(mid, session=session)
        zfwbtext.update(values)
        zfwbtext.save(session=session)

    return zfwbtext_get_by_mid(mid)


def zfwbtext_delete(id, session=None):
    if not session:
        session = get_session()

    zfwbtexts = zfwbtext_get_by_id(id)
    for zfwbtext in zfwbtexts:
        zfwbtext.delete(session)


def zfwbtext_delete_mid(mid, session=None):
    if not session:
        session = get_session()

    zfwbtext = zfwbtext_get_by_mid(mid)
    if zfwbtext:
        zfwbtext.delete(session)


def zfwbtext_delete_uid(uid, session=None):
    if not session:
        session = get_session()

    zfwbtexts = zfwbtext_get_by_uid(uid)
    for zfwbtext in zfwbtexts:
        zfwbtext.delete(session)


def zfwbtext_get_by_id(id, session=None):
    result = model_query(models.Zfwbtext, session=session).\
                     filter_by(id=id).\
                     first()
    if not result:
        raise exception.zfwbtextIdNotFound(id=id)

    return result


def zfwbtext_get_by_mid(mid, session=None):
    result = model_query(models.Zfwbtext, session=session).\
                     filter_by(mid=mid).\
                     first()
    if not result:
        raise exception.ZfwbtextMidNotFound(mid=mid)

    return result


def zfwbtext_get_by_uid(uid, session=None):
    result = model_query(models.Zfwbtext, session=session).\
                     filter_by(uid=uid).\
                     all()
    if not result:
        raise exception.zfwbtextUidNotFound(uid=uid)

    return result


def zfwbtext_get_by_mid_and_zf(mid, is_zf=False, session=None):
    result = model_query(models.Zfwbtext, session=session).\
                     filter_by(mid=mid).\
                     filter_by(is_zf=is_zf).\
                     first()

    if not result:
        raise exception.zfwbtextMidAndZfNotFound(mid=mid,
                                                 is_zf=is_zf)

    return result


# --------------services options ---------------------------#
def _service_get(service_id, session=None):
    query = model_query(models.Service, session=session).\
        filter_by(id=service_id)

    result = query.first()
    if not result:
        raise exception.ServiceNotFound(service_id=service_id)

    return result


def service_get(service_id, use_slave=False):
    return _service_get(service_id)


def service_get_by_args(host, binary, session=None):
    result = model_query(models.Service, session=session).\
                     filter_by(host=host).\
                     filter_by(binary=binary).\
                     first()
    if not result:
        raise exception.NotFound()

    return result


def service_create(values):
    service_ref = models.Service()
    service_ref.update(values)
    try:
        service_ref.save()
    except exception.DBDuplicateEntry as e:
        if 'binary' in e.columns:
            raise exception.ServiceBinaryExists(host=values.get('host'),
                                                binary=values.get('binary'))
        raise exception.ServiceTopicExists(host=values.get('host'),
                                           topic=values.get('topic'))
    return service_ref


def service_update(service_id, values):
    session = get_session()
    with session.begin():
        service_ref = _service_get(service_id, session=session)
        # Only servicegroup.drivers.db.DbDriver._report_state() updates
        # 'report_count', so if that value changes then store the timestamp
        # as the last time we got a state report.
        if 'report_count' in values:
            if values['report_count'] > service_ref.report_count:
                service_ref.last_seen_up = timeutils.utcnow()
        service_ref.update(values)

    return service_ref


def service_get_all(disabled=None):
    query = model_query(models.Service)

    if disabled is not None:
        query = query.filter_by(disabled=disabled)

    return query.all()
