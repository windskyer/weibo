#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2016
# author: zwei
'''
Crawler same weibo info
'''

import os
import sys

import weibo
from weibo import simu
from weibo.common import cfg
from weibo.common import log


CONF = cfg.CONF


def set_env():
    possible_topdir = os.path.normpath(os.path.join(os.path.abspath(__file__),
                                                    os.pardir,
                                                    os.pardir,
                                                    os.pardir))
    if os.path.exists(os.path.join(possible_topdir,
                                   "weibo",
                                   "__init__.py")):
        sys.path.insert(0, possible_topdir)

    dev_conf = os.path.join(possible_topdir,
                            'etc',
                            'weibo.conf')
    if os.path.exists(dev_conf):
        CONF(dev_conf)
    else:
        CONF()
        # LOG = logging.setup(*argv[:-1])


def api():
    # API 参考 http://open.weibo.com/wiki/%E5%BE%AE%E5%8D%9AAPI
    # 使用参考 https://github.com/lxyu/weibo
    api = weibo.useAPI()
    # print(api.get('statuses/user_timeline'))
    # print(api.get('statuses/user_timeline/ids'))
    print(api.get('statuses/queryid', mid="1035051413304027"))
    # print(api.post('statuses/update', status='test from my api'))


def login():
    # 首先登入
    simu.Simu.check_login()

    # 模拟登陆的功能扩展待完善
    simulogin = simu.Simu()

    print(simulogin.detail())
    #print(simulogin.detail('http://weibo.com/kaifulee'))


def pweibo():
    pass


def pmain():
    set_env()
    login()


def amain():
    api()


if __name__ == '__main__':
    pmain()
