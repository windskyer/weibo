# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Time related utilities and helper functions.
"""

import calendar
import datetime
import iso8601
from monotonic import monotonic as now

from weibo.common import reflection

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
PERFECT_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"


def isotime(at=None):
    """Stringify time in ISO 8601 format"""
    if not at:
        at = utcnow()
    str = at.strftime(TIME_FORMAT)
    tz = at.tzinfo.tzname(None) if at.tzinfo else 'UTC'
    str += ('Z' if tz == 'UTC' else tz)
    return str


def parse_isotime(timestr):
    """Parse time from ISO 8601 format"""
    try:
        return iso8601.parse_date(timestr)
    except iso8601.ParseError as e:
        raise ValueError(e.message)
    except TypeError as e:
        raise ValueError(e.message)


def strtime(at=None, fmt=PERFECT_TIME_FORMAT):
    """Returns formatted utcnow."""
    if not at:
        at = utcnow()
    return at.strftime(fmt)


def parse_strtime(timestr, fmt=PERFECT_TIME_FORMAT):
    """Turn a formatted time back into a datetime."""
    return datetime.datetime.strptime(timestr, fmt)


def normalize_time(timestamp):
    """Normalize time in arbitrary timezone to UTC"""
    offset = timestamp.utcoffset()
    return timestamp.replace(tzinfo=None) - offset if offset else timestamp


def is_older_than(before, seconds):
    """Return True if before is older than seconds."""
    return utcnow() - before > datetime.timedelta(seconds=seconds)


def utcnow_ts():
    """Timestamp version of our utcnow function."""
    return calendar.timegm(utcnow().timetuple())


def utcnow():
    """Overridable version of utils.utcnow."""
    if utcnow.override_time:
        return utcnow.override_time
    return datetime.datetime.utcnow()


utcnow.override_time = None


def set_time_override(override_time=datetime.datetime.utcnow()):
    """Override utils.utcnow to return a constant time."""
    utcnow.override_time = override_time


def advance_time_delta(timedelta):
    """Advance overridden time using a datetime.timedelta."""
    assert(utcnow.override_time is not None)
    utcnow.override_time += timedelta


def advance_time_seconds(seconds):
    """Advance overridden time by seconds."""
    advance_time_delta(datetime.timedelta(0, seconds))


def clear_time_override():
    """Remove the overridden time."""
    utcnow.override_time = None


def marshall_now(now=None):
    """Make an rpc-safe datetime with microseconds.

    Note: tzinfo is stripped, but not required for relative times."""
    if not now:
        now = utcnow()
    return dict(day=now.day, month=now.month, year=now.year, hour=now.hour,
                minute=now.minute, second=now.second,
                microsecond=now.microsecond)


def unmarshall_time(tyme):
    """Unmarshall a datetime dict."""
    return datetime.datetime(day=tyme['day'],
                             month=tyme['month'],
                             year=tyme['year'],
                             hour=tyme['hour'],
                             minute=tyme['minute'],
                             second=tyme['second'],
                             microsecond=tyme['microsecond'])


class Split(object):
    """A *immutable* stopwatch split.

    See: http://en.wikipedia.org/wiki/Stopwatch for what this is/represents.

    .. versionadded:: 1.4
    """

    __slots__ = ['_elapsed', '_length']

    def __init__(self, elapsed, length):
        self._elapsed = elapsed
        self._length = length

    @property
    def elapsed(self):
        """Duration from stopwatch start."""
        return self._elapsed

    @property
    def length(self):
        """Seconds from last split (or the elapsed time if no prior split)."""
        return self._length

    def __repr__(self):
        r = reflection.get_class_name(self, fully_qualified=False)
        r += "(elapsed=%s, length=%s)" % (self._elapsed, self._length)
        return r


class StopWatch(object):
    """A simple timer/stopwatch helper class.

    Inspired by: apache-commons-lang java stopwatch.

    Not thread-safe (when a single watch is mutated by multiple threads at
    the same time). Thread-safe when used by a single thread (not shared) or
    when operations are performed in a thread-safe manner on these objects by
    wrapping those operations with locks.

    It will use the `monotonic`_ pypi library to find an appropriate
    monotonically increasing time providing function (which typically varies
    depending on operating system and python version).

    .. _monotonic: https://pypi.python.org/pypi/monotonic/

    .. versionadded:: 1.4
    """
    _STARTED = 'STARTED'
    _STOPPED = 'STOPPED'

    def __init__(self, duration=None):
        if duration is not None and duration < 0:
            raise ValueError("Duration must be greater or equal to"
                             " zero and not %s" % duration)
        self._duration = duration
        self._started_at = None
        self._stopped_at = None
        self._state = None
        self._splits = []

    def start(self):
        """Starts the watch (if not already started).

        NOTE(harlowja): resets any splits previously captured (if any).
        """
        if self._state == self._STARTED:
            return self
        self._started_at = now()
        self._stopped_at = None
        self._state = self._STARTED
        self._splits = []
        return self

    @property
    def splits(self):
        """Accessor to all/any splits that have been captured."""
        return tuple(self._splits)

    def split(self):
        """Captures a split/elapsed since start time (and doesn't stop)."""
        if self._state == self._STARTED:
            elapsed = self.elapsed()
            if self._splits:
                length = self._delta_seconds(self._splits[-1].elapsed, elapsed)
            else:
                length = elapsed
            self._splits.append(Split(elapsed, length))
            return self._splits[-1]
        else:
            raise RuntimeError("Can not create a split time of a stopwatch"
                               " if it has not been started or if it has been"
                               " stopped")

    def restart(self):
        """Restarts the watch from a started/stopped state."""
        if self._state == self._STARTED:
            self.stop()
        self.start()
        return self

    @staticmethod
    def _delta_seconds(earlier, later):
        # Uses max to avoid the delta/time going backwards (and thus negative).
        return max(0.0, later - earlier)

    def elapsed(self, maximum=None):
        """Returns how many seconds have elapsed."""
        if self._state not in (self._STARTED, self._STOPPED):
            raise RuntimeError("Can not get the elapsed time of a stopwatch"
                               " if it has not been started/stopped")
        if self._state == self._STOPPED:
            elapsed = self._delta_seconds(self._started_at, self._stopped_at)
        else:
            elapsed = self._delta_seconds(self._started_at, now())
        if maximum is not None and elapsed > maximum:
            elapsed = max(0.0, maximum)
        return elapsed

    def __enter__(self):
        """Starts the watch."""
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        """Stops the watch (ignoring errors if stop fails)."""
        try:
            self.stop()
        except RuntimeError:  # nosec: errors are meant to be ignored
            pass

    def leftover(self, return_none=False):
        """Returns how many seconds are left until the watch expires.

        :param return_none: when ``True`` instead of raising a ``RuntimeError``
                            when no duration has been set this call will
                            return ``None`` instead.
        :type return_none: boolean
        """
        if self._state != self._STARTED:
            raise RuntimeError("Can not get the leftover time of a stopwatch"
                               " that has not been started")
        if self._duration is None:
            if not return_none:
                raise RuntimeError("Can not get the leftover time of a watch"
                                   " that has no duration")
            return None
        return max(0.0, self._duration - self.elapsed())

    def expired(self):
        """Returns if the watch has expired (ie, duration provided elapsed)."""
        if self._state not in (self._STARTED, self._STOPPED):
            raise RuntimeError("Can not check if a stopwatch has expired"
                               " if it has not been started/stopped")
        if self._duration is None:
            return False
        return self.elapsed() > self._duration

    def has_started(self):
        return self._state == self._STARTED

    def has_stopped(self):
        return self._state == self._STOPPED

    def resume(self):
        """Resumes the watch from a stopped state."""
        if self._state == self._STOPPED:
            self._state = self._STARTED
            return self
        else:
            raise RuntimeError("Can not resume a stopwatch that has not been"
                               " stopped")

    def stop(self):
        """Stops the watch."""
        if self._state == self._STOPPED:
            return self
        if self._state != self._STARTED:
            raise RuntimeError("Can not stop a stopwatch that has not been"
                               " started")
        self._stopped_at = now()
        self._state = self._STOPPED
        return self
