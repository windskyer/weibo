#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2013
#
__author__ = 'zwei'

import sys

import weibo

def apiExample():
    # API 参考 http://open.weibo.com/wiki/%E5%BE%AE%E5%8D%9AAPI
    # 使用参考 https://github.com/lxyu/weibo
    api = weibo.useAPI()
    #print(api.get('statuses/user_timeline'))
    #print(api.get('statuses/user_timeline/ids'))
    print(api.get('statuses/queryid', mid="1035051413304027"))
    #print(api.post('statuses/update', status='test from my api'))

def simuLogin():
    # 模拟登陆的功能扩展待完善
    simu = weibo.simu()

    # 首先认证登入
    simu.pre_weibo_login

    # 验证登入
    if simu.check_login:
        sys.exit(1)
    print(simu.detail())
    #print(simu.detail('http://weibo.com/kaifulee'))

if __name__ == '__main__':
    simuLogin()
    #apiExample()
