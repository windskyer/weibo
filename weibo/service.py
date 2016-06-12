"""Generic Weibo base class for all workers that run on hosts."""

import errno
import inspect
import os
import random
import signal
import sys
import time

import eventlet
import greenlet

