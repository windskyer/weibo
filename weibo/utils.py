import os
import sys
import time
import urlparse
import urllib2
from eventlet import event
from eventlet.green import subprocess
from eventlet import greenthread

from weibo import exception
from weibo.common.gettextutils import _
from weibo.common import jsonutils
from weibo.common import log as logging

LOG = logging.getLogger(__name__)


def conn_img_url(bigurl, ntime=3):
    while ntime > 0:
        try:
            time.sleep(3)
            urllib2.urlopen(bigurl)
        except Exception:
            ntime = ntime - 1
        else:
            break

    if ntime < 1:
        raise exception.ConnNotUrl(url=bigurl)


def exists_big_img(url):
    jxurl = urlparse.urlparse(url)
    path = jxurl.path
    netloc = jxurl.netloc
    dirname, filename = os.path.split(path)
    baseurl = jxurl.scheme + '://' + netloc
    if 'sinaimg' in netloc:
        dirname = '/mw690'
        path = dirname + '/' + filename
        bigurl = urlparse.urljoin(baseurl, path)
        try:
            conn_img_url(bigurl)
        except exception.ConnNotUrl:
            return
    else:
        return bigurl


def read_cached_file(filename, cache_info, reload_func=None):
    """Read from a file if it has been modified.

    :param cache_info: dictionary to hold opaque cache.
    :param reload_func: optional function to be called with data when
                        file is reloaded due to a modification.

    :returns: data from file

    """
    mtime = os.path.getmtime(filename)
    if not cache_info or mtime != cache_info.get('mtime'):
        LOG.debug(_("Reloading cached file %s") % filename)
        with open(filename) as fap:
            cache_info['data'] = fap.read()
        cache_info['mtime'] = mtime
        if reload_func:
            reload_func(cache_info['data'])
    return jsonutils.loads(cache_info['data'])


def to_bytes(s):
    if bytes != str:
        if type(s) == str:
            return s.encode('utf-8')
    return s


def to_str(s):
    if bytes != str:
        if type(s) == bytes:
            return s.decode('utf-8')
    return s


def debug(arg):
    LOG.debug(_('debug in callback: %s'), arg)
    return arg


def str_dict_replace(s, mapping):
    for s1, s2 in mapping.iteritems():
        s = s.replace(s1, s2)
    return s


def diff_dict(orig, new):
    """
    Return a dict describing how to change orig to new.  The keys
    correspond to values that have changed; the value will be a list
    of one or two elements.  The first element of the list will be
    either '+' or '-', indicating whether the key was updated or
    deleted; if the key was updated, the list will contain a second
    element, giving the updated value.
    """
    # Figure out what keys went away
    result = dict((k, ['-']) for k in set(orig.keys()) - set(new.keys()))
    # Compute the updates
    for key, value in new.items():
        if key not in orig or value != orig[key]:
            result[key] = ['+', value]
    return result


class LoopingCallDone(Exception):
    """Exception to break out and stop a LoopingCall.

    The poll-function passed to LoopingCall can raise this exception to
    break out of the loop normally. This is somewhat analogous to
    StopIteration.

    An optional return-value can be included as the argument to the exception;
    this return-value will be returned by LoopingCall.wait()

    """

    def __init__(self, retvalue=True):
        """:param retvalue: Value that LoopingCall.wait() should return."""
        self.retvalue = retvalue


class LoopingCall(object):
    def __init__(self, f=None, *args, **kw):
        self.args = args
        self.kw = kw
        self.f = f
        self._running = False

    def start(self, interval, initial_delay=None):
        self._running = True
        done = event.Event()

        def _inner():
            if initial_delay:
                greenthread.sleep(initial_delay)

            try:
                while self._running:
                    self.f(*self.args, **self.kw)
                    if not self._running:
                        break
                    greenthread.sleep(interval)
            except LoopingCallDone, e:
                self.stop()
                done.send(e.retvalue)
            except Exception:
                LOG.exception(_('in looping call'))
                done.send_exception(*sys.exc_info())
                return
            else:
                done.send(True)

        self.done = done

        greenthread.spawn(_inner)
        return self.done

    def stop(self):
        self._running = False

    def wait(self):
        return self.done.wait()
