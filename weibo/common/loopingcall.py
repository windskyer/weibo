import sys

from eventlet import event
from eventlet import greenthread

from weibo.common.gettextutils import _, _LE, _LW
from weibo.common import reflection
from weibo.common import timeutils
from weibo.common import log as logging

LOG = logging.getLogger(__name__)


class LoopingCallDone(Exception):
    """Exception to break out and stop a LoopingCallBase.

    The poll-function passed to LoopingCallBase can raise this exception to
    break out of the loop normally. This is somewhat analogous to
    StopIteration.

    An optional return-value can be included as the argument to the exception;
    this return-value will be returned by LoopingCallBase.wait()

    """

    def __init__(self, retvalue=True):
        """:param retvalue: Value that LoopingCallBase.wait() should return."""
        self.retvalue = retvalue


class LoopingCallTimeOut(Exception):
    """Exception for a timed out LoopingCall.

    The LoopingCall will raise this exception when a timeout is provided
    and it is exceeded.
    """
    pass


def _safe_wrapper(f, kind, func_name):
    """Wrapper that calls into wrapped function and logs errors as needed."""

    def func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except LoopingCallDone:
            raise  # let the outer handler process this
        except Exception:
            LOG.error(_LE('%(kind)s %(func_name)r failed'),
                      {'kind': kind, 'func_name': func_name},
                      exc_info=True)
            return 0

    return func


class LoopingCallBase(object):
    _KIND = _("Unknown looping call")

    _RUN_ONLY_ONE_MESSAGE = _("A looping call can only run one function"
                              " at a time")

    def __init__(self, f=None, *args, **kw):
        self.args = args
        self.kw = kw
        self.f = f
        self._running = False
        self._thread = None
        self.done = None

    def stop(self):
        self._running = False

    def wait(self):
        return self.done.wait()

    def _on_done(self, gt, *args, **kwargs):
        self._thread = None
        self._running = False

    def _start(self, idle_for, initial_delay=None, stop_on_exception=True):
        """Start the looping

        :param idle_for: Callable that takes two positional arguments, returns
                         how long to idle for. The first positional argument is
                         the last result from the function being looped and the
                         second positional argument is the time it took to
                         calculate that result.
        :param initial_delay: How long to delay before starting the looping.
                              Value is in seconds.
        :param stop_on_exception: Whether to stop if an exception occurs.
        :returns: eventlet event instance
        """
        if self._thread is not None:
            raise RuntimeError(self._RUN_ONLY_ONE_MESSAGE)
        self._running = True
        self.done = event.Event()
        self._thread = greenthread.spawn(
            self._run_loop, idle_for,
            initial_delay=initial_delay,
            stop_on_exception=stop_on_exception)
        self._thread.link(self._on_done)
        return self.done

    def _run_loop(self, idle_for_func,
                  initial_delay=None,
                  stop_on_exception=True):
        kind = self._KIND
        func_name = reflection.get_callable_name(self.f)
        func = self.f if stop_on_exception else _safe_wrapper(self.f, kind,
                                                              func_name)
        if initial_delay:
            greenthread.sleep(initial_delay)
        try:
            watch = timeutils.StopWatch()
            while self._running:
                watch.restart()
                result = func(*self.args, **self.kw)
                watch.stop()
                if not self._running:
                    break
                idle = idle_for_func(result, watch.elapsed())
                LOG.trace('%(kind)s %(func_name)r sleeping '
                          'for %(idle).02f seconds',
                          {'func_name': func_name, 'idle': idle,
                           'kind': kind})
                greenthread.sleep(idle)
        except LoopingCallDone as e:
            self.done.send(e.retvalue)
        except Exception:
            exc_info = sys.exc_info()
            try:
                LOG.error(_LE('%(kind)s %(func_name)r failed'),
                          {'kind': kind, 'func_name': func_name},
                          exc_info=exc_info)
                self.done.send_exception(*exc_info)
            finally:
                del exc_info
            return
        else:
            self.done.send(True)


class FixedIntervalLoopingCall(LoopingCallBase):
    """A fixed interval looping call."""

    _RUN_ONLY_ONE_MESSAGE = _("A fixed interval looping call can only run"
                              " one function at a time")

    _KIND = _('Fixed interval looping call')

    def start(self, interval, initial_delay=None, stop_on_exception=True):
        def _idle_for(result, elapsed):
            delay = round(elapsed - interval, 2)
            if delay > 0:
                func_name = reflection.get_callable_name(self.f)
                LOG.warning(_LW('Function %(func_name)r run outlasted '
                                'interval by %(delay).2f sec'),
                            {'func_name': func_name, 'delay': delay})
            return -delay if delay < 0 else 0
        return self._start(_idle_for, initial_delay=initial_delay,
                           stop_on_exception=stop_on_exception)


class DynamicLoopingCall(LoopingCallBase):
    """A looping call which sleeps until the next known event.

    The function called should return how long to sleep for before being
    called again.
    """

    _RUN_ONLY_ONE_MESSAGE = _("A dynamic interval looping call can only run"
                              " one function at a time")
    _TASK_MISSING_SLEEP_VALUE_MESSAGE = _(
        "A dynamic interval looping call should supply either an"
        " interval or periodic_interval_max"
    )

    _KIND = _('Dynamic interval looping call')

    def start(self, initial_delay=None, periodic_interval_max=None,
              stop_on_exception=True):
        def _idle_for(suggested_delay, elapsed):
            delay = suggested_delay
            if delay is None:
                if periodic_interval_max is not None:
                    delay = periodic_interval_max
                else:
                    # Note(suro-patz): An application used to receive a
                    #     TypeError thrown from eventlet layer, before
                    #     this RuntimeError was introduced.
                    raise RuntimeError(
                        self._TASK_MISSING_SLEEP_VALUE_MESSAGE)
            else:
                if periodic_interval_max is not None:
                    delay = min(delay, periodic_interval_max)
            return delay

        return self._start(_idle_for, initial_delay=initial_delay,
                           stop_on_exception=stop_on_exception)
