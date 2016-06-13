# --*-- coding: utf-8 --*--

import eventlet
eventlet.monkey_patch()

from weibo import service
from weibo.api import api

from weibo.common import cfg
from weibo.common import log as logging

CONF = cfg.CONF


class Client(objct):
    def __init__(self, conf, *args, **kwargs):
        if not conf:
            try:
                conf = CONF.api1
            except:
                raise exception.AppkeyError()
        useapi = api.useAPI(conf)

    @classmethod
    def create(cls, report_interval=None, periodic_interval=None):
        """Instantiates class and passes back application object.

        :param report_interval: defaults to FLAGS.report_interval
        :param periodic_interval: defaults to FLAGS.periodic_interval
        :param periodic_fuzzy_delay: defaults to FLAGS.periodic_fuzzy_delay

        """
        pass


    def start(self):
        pass

    def run(self):
        pass

    def wait(self):
        pass

    def stop(self):
        pass

    def kill(self):
        pass


def main():
    api_keys = CONF.api_key
    launcher = service.ProcessLauncher()
    for api_key in api_keys:
        conf = CONF.api_key
        client = Client(conf)
        server.create()
        launcher.launch_server(server)

    launcher.wait()
