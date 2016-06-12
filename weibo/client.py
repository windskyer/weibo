# --*-- coding: utf-8 --*--

from weibo import server
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
    for api_key in api_keys:
        server.create(Client(CONF[api_key]))
