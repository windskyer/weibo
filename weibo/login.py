# --*-- coding: utf-8 --*--
# author: zwei
# email: suifeng20@hotmail.com

import os
import re
import six
import rsa
import json
import base64
import binascii
import hashlib
import urllib

try:
    import urllib2
except Exception:
    import urllib.request as urllib2
try:
    import cookielib
except Exception:
    import http.cookiejar as cookielib

from weibo import exception
from weibo.common import cfg
from weibo.common import log

CONF = cfg.CONF


class BaseLogin(object):
    '''
    Create base class
    '''
    def __init__(self, username, pwd, cookie_file=None):
        if not username:
            self.username = CONF.username
        if not pwd:
            self.pwd = CONF.password
        if not cookie_file:
            self.cookie_file = CONF.cookie_file


class Login(BaseLogin):
    '''
    Created on Mar 18, 2013

    @author: yoyzhou
    '''

    '''
    Updated on APril 16, 2014

    @author: wanghaisheng
    '''

    '''
    Updated on APril 16, 2016
    @author: zwei
    '''

    def __init__(self, username, pwd, cookie_file=None):
        self.username = username
        self.pwd = pwd
        self.cookie_file = cookie_file
        super(Login, self).__init__(username, pwd)
        self.login(self.username, self.pwd, self.cookie_file)

    def getHTML(self, url):
        """
        Get specifer url html
        """
        return urllib2.urlopen(url).read()

    def get_prelogin_status(self, username):
        """
        Perform prelogin action,
        get prelogin status,
        including servertime,
        nonce, rsakv, etc.
        """
        # prelogin_url = ('http://login.sina.com.cn/sso/prelogin.php'
        #                '?entry=weibo&callback=sinaSSOController.preloginCallBack&client=ssologin.js(v1.4.5)'
        prelogin_url = ('http://login.sina.com.cn/sso/prelogin.php'
                        '?entry=weibo'
                        '&callback=sinaSSOController.preloginCallBack'
                        '&su=' + self.get_user(username) +
                        '&rsakt=mod&checkpin=1'
                        '&client=ssologin.js(v1.4.11)')

        data = urllib2.urlopen(prelogin_url).read()
        p = re.compile('\((.*)\)')
        data = data.decode('utf-8')

        try:
            json_data = p.search(data).group(1)
            data = json.loads(json_data)
            servertime = str(data['servertime'])
            nonce = data['nonce']
            rsakv = data['rsakv']
            return servertime, nonce, rsakv
        except:
            print('Getting prelogin status met error!')
            return None

    def login(self, username, pwd, cookie_file):
        """"
            Login with use name, password and cookies.
            (1) If cookie file exists then try to load cookies;
            (2) If no cookies found then do login
        """
        # If cookie file exists then try to load cookies
        if os.path.exists(cookie_file):
            try:
                cookie_jar = cookielib.LWPCookieJar(cookie_file)
                cookie_jar.load(ignore_discard=True, ignore_expires=True)
                loaded = 1
            except cookielib.LoadError:
                loaded = 0
                print('Loading cookies error')

            # install loaded cookies for urllib2
            if loaded:
                cookie_support = urllib2.HTTPCookieProcessor(cookie_jar)
                opener = urllib2.build_opener(cookie_support,
                                              urllib2.HTTPHandler)
                urllib2.install_opener(opener)
                print('Loading cookies success')
                return 1
            else:
                return self.do_login(username, pwd, cookie_file)

        else:  # If no cookies found
            return self.do_login(username, pwd, cookie_file)

    def do_login(self, username, pwd, cookie_file):
        """"
        Perform login action with use name, password and saving cookies.
        @param username: login user name
        @param pwd: login password
        @param cookie_file: file name where to save cookies
                            when login succeeded
        """
        # POST data per LOGIN WEIBO,
        # these fields can be captured using httpfox extension in FIrefox
        ajaxurl = ('http://weibo.com/ajaxlogin.php'
                   '?framelogin=1'
                   '&callback=parent.sinaSSOController.feedBackUrlCallBack')
        login_data = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'userticket': '1',
            'pagerefer': '',
            'vsnf': '1',
            'su': '',
            'service': 'miniblog',
            'servertime': '',
            'nonce': '',
            'pwencode': 'rsa2',
            'rsakv': '',
            'sp': '',
            'encoding': 'UTF-8',
            'prelt': '45',
            'url': ajaxurl,
            'returntype': 'META'
        }

        cookie_jar2 = cookielib.LWPCookieJar()
        cookie_support2 = urllib2.HTTPCookieProcessor(cookie_jar2)
        opener2 = urllib2.build_opener(cookie_support2, urllib2.HTTPHandler)
        urllib2.install_opener(opener2)
        login_url = ('http://login.sina.com.cn/sso/login.php'
                     '?client=ssologin.js(v1.4.11)')
        try:
            servertime, nonce, rsakv = self.get_prelogin_status(username)
        except:
            return

        # Fill POST data
        print('starting to set login_data')
        login_data['servertime'] = servertime
        login_data['nonce'] = nonce
        login_data['su'] = self.get_user(username)
        login_data['sp'] = self.get_pwd_rsa(pwd, servertime, nonce)
        login_data['rsakv'] = rsakv
        if six.PY3:
            login_data = urllib.parse.urlencode(login_data)
            login_data = login_data.encode()
        else:
            login_data = urllib.urlencode(login_data)

        User_Agent = ('Mozilla/5.0 '
                      '(X11; Linux i686; rv:8.0) '
                      'Gecko/20100101 Firefox/8.0')

        http_headers = {'User-Agent': User_Agent}
        req_login = urllib2.Request(
            url=login_url,
            data=login_data,
            headers=http_headers
        )
        result = urllib2.urlopen(req_login)
        text = result.read()
        if six.PY3:
            text = text.decode('gbk')
        p = re.compile('location\.replace\(\'(.*?)\'\)')
        # 在使用httpfox登录调试时，我获取的返回参数
        # location.replace('http://weibo.com 这里使用的是单引号
        # 原来的正则中匹配的是双引号# 导致没有login_url得到 单引号本身在re中无需转义
        # p = re.compile('location\.replace\(\B'(.*?)'\B\)')
        # 经调试 这样子是错误的 re中非的使用\'才能表达单引号
        try:
            # Search login redirection URL
            login_url = p.search(text).group(1)
            data = urllib2.urlopen(login_url).read()
            # Verify login feedback, check whether result is TRUE
            patt_feedback = 'feedBackUrlCallBack\((.*)\)'
            p = re.compile(patt_feedback, re.MULTILINE)

            feedback = p.search(data).group(1)
            feedback_json = json.loads(feedback)
            if feedback_json['result']:
                cookie_jar2.save(cookie_file,
                                 ignore_discard=True,
                                 ignore_expires=True)
                return 1
            else:
                return 0
        except:
            return 0

    def get_pwd_wsse(self, pwd, servertime, nonce):
        """
        Get wsse encrypted password
        """
        pwd1 = hashlib.sha1(pwd).hexdigest()
        pwd2 = hashlib.sha1(pwd1).hexdigest()
        pwd3_ = pwd2 + servertime + nonce
        pwd3 = hashlib.sha1(pwd3_).hexdigest()
        return pwd3

    def get_pwd_rsa(self, pwd, servertime, nonce):
        """
        Get rsa2 encrypted password,
        using RSA module from https://pypi.python.org/pypi/rsa/3.1.1,
        documents can be accessed at
        http://stuvel.eu/files/python-rsa-doc/index.html
        """

        # n, n parameter of RSA public key,
        # which is published by WEIBO.COM
        # hardcoded here but you can also find
        # it from values return from prelogin status above

        weibo_rsa_n = ('EB2A38568661887FA180BDDB5CABD5F21C7BFD59C090'
                       'CB2D245A87AC253062882729293E5506350508E7F9AA'
                       '3BB77F4333231490F915F6D63C55FE2F08A49B353F44'
                       '4AD3993CACC02DB784ABBB8E42A9B1BBFFFB38BE18D7'
                       '8E87A0E41B9B8F73A928EE0CCEE1F6739884B9777E4F'
                       'E9E88A1BBE495927AC4A799B3181D6442443')

        # e, exponent parameter of RSA public key,
        # WEIBO uses 0x10001, which is 65537 in Decimal
        weibo_rsa_e = 65537
        message = str(servertime) + '\t' + str(nonce) + '\n' + str(pwd)

        # construct WEIBO RSA Publickey using n and e above,
        # note that n is a hex string
        key = rsa.PublicKey(int(weibo_rsa_n, 16), weibo_rsa_e)

        # get encrypted password
        if six.PY3:
            message = message.encode()

        encropy_pwd = rsa.encrypt(message, key)
        # trun back encrypted password binaries to hex string
        sp = binascii.b2a_hex(encropy_pwd)
        if six.PY3:
            sp = sp.decode('utf-8')

        return sp

    def get_user(self, username):
        username_ = urllib2.quote(username)
        if six.PY3:
            username = base64.encodestring(username_.encode())[:-1]
            username = username.decode('utf-8')

        if six.PY2:
            username = base64.encodestring(username_)[:-1]

        return username
