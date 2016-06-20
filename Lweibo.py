#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2013
#

__author__ = 'zwei'

import io
import os
import sys
import re
import six
try:
    import ConfigParser
except:
    import configparser as ConfigParser
import webbrowser
import json
import time
import urllib
try:
    import urllib2
except:
    import urllib.request as urllib2
import requests
try:
    import cookielib
except:
    import http.cookiejar as cookielib
import hashlib
import binascii
import rsa
import base64
import datetime

try:
    import cPickle as pkl
except:
    import pickle as pkl


class Client(object):
    """Python sina weibo sdk.

    Rely on `requests` to do the dirty work, so it's much simpler and cleaner
    than the official SDK.

    For more info, refer to:
    http://lxyu.github.com/weibo/
    """

    def __init__(self, api_key, api_secret, redirect_uri, token=None):
        # const define
        self.site = 'https://api.weibo.com/'
        self.authorization_url = self.site + 'oauth2/authorize'
        self.token_url = self.site + 'oauth2/access_token'
        self.api_url = self.site + '2/'

        # init basic info
        self.client_id = api_key
        self.client_secret = api_secret
        self.redirect_uri = redirect_uri

        self.session = requests.session()

        # activate client directly if given token
        if token:
            self.set_token(token)

    @property
    def authorize_url(self):
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri
        }
        try:
            # for python2.x
            urlencode = urllib.urlencode(params)
        except:
            urlencode = urllib.parse.urlencode(params)
        return "{0}?{1}".format(
            self.authorization_url, urlencode)

    @property
    def alive(self):
        if self.expires_at:
            return self.expires_at > time.time()
        else:
            return False

    def set_code(self, authorization_code):
        """Activate client by authorization_code.
        """
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'redirect_uri': self.redirect_uri
        }
        res = requests.post(self.token_url, data=params)
        token = json.loads(res.text)
        self._assert_error(token)

        token[u'expires_at'] = int(time.time()) + int(token.pop(u'expires_in'))
        self.set_token(token)

    def set_token(self, token):
        """Directly activate client by access_token.
        """
        self.token = token

        self.uid = token['uid']
        self.access_token = token['access_token']
        self.expires_at = token['expires_at']

        self.session.params = {'access_token': self.access_token}

    def _assert_error(self, d):
        """Assert if json response is error.
        """
        if 'error_code' in d and 'error' in d:
            raise RuntimeError("{0} {1}".format(
                d.get("error_code", ""), d.get("error", "")))

    def get(self, uri, **kwargs):
        """Request resource by get method.
        """
        url = "{0}{1}.json".format(self.api_url, uri)
        res = json.loads(self.session.get(url, params=kwargs).text)
        self._assert_error(res)
        return res

    def post(self, uri, **kwargs):
        """Request resource by post method.
        """
        url = "{0}{1}.json".format(self.api_url, uri)
        if "pic" not in kwargs:
            res = json.loads(self.session.post(url, data=kwargs).text)
        else:
            files = {"pic": kwargs.pop("pic")}
            res = json.loads(self.session.post(url,
                                               data=kwargs,
                                               files=files).text)
        self._assert_error(res)
        return res


class weibo_login(object):
    '''
    Created on Mar 18, 2013

    @author: yoyzhou
    '''

    '''
    Updated on APril 16, 2014

    @author: wanghaisheng
    '''

    def __init__(self, username, pwd, cookie_file='/tmp/weibo_login_cookies.dat'):
        self.login(username, pwd, cookie_file)

    def getHTML(self, url):
        return urllib2.urlopen(url).read()

    def get_prelogin_status(self, username):
        """
        Perform prelogin action, get prelogin status, including servertime, nonce, rsakv, etc.
        """
        # prelogin_url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&client=ssologin.js(v1.4.5)'
        #import pdb;pdb.set_trace()
        prelogin_url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=' + self.get_user(
            username) + \
                       '&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.11)';
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

            #install loaded cookies for urllib2
            if loaded:
                cookie_support = urllib2.HTTPCookieProcessor(cookie_jar)
                opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
                urllib2.install_opener(opener)
                print('Loading cookies success')
                return 1
            else:
                return self.do_login(username, pwd, cookie_file)

        else:  #If no cookies found
            return self.do_login(username, pwd, cookie_file)


    def do_login(self, username, pwd, cookie_file):
        """"
        Perform login action with use name, password and saving cookies.
        @param username: login user name
        @param pwd: login password
        @param cookie_file: file name where to save cookies when login succeeded
        """
        # POST data per LOGIN WEIBO, these fields can be captured using httpfox extension in FIrefox
        import pdb;pdb.set_trace()
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
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META'
        }

        cookie_jar2 = cookielib.LWPCookieJar()
        cookie_support2 = urllib2.HTTPCookieProcessor(cookie_jar2)
        opener2 = urllib2.build_opener(cookie_support2, urllib2.HTTPHandler)
        urllib2.install_opener(opener2)
        login_url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.11)'
        try:
            servertime, nonce, rsakv = self.get_prelogin_status(username)
        except:
            return

        #Fill POST data
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
        http_headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0'}
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
        #在使用httpfox登录调试时，我获取的返回参数  location.replace('http://weibo.com 这里使用的是单引号 原来的正则中匹配的是双引号# 导致没有login_url得到 单引号本身在re中无需转义
        #p = re.compile('location\.replace\(\B'(.*?)'\B\)') 经调试 这样子是错误的 re中非的使用\'才能表达单引号
        try:
            #Search login redirection URL
            login_url = p.search(text).group(1)
            data = urllib2.urlopen(login_url).read()
            #Verify login feedback, check whether result is TRUE
            patt_feedback = 'feedBackUrlCallBack\((.*)\)'
            p = re.compile(patt_feedback, re.MULTILINE)

            feedback = p.search(data).group(1)
            feedback_json = json.loads(feedback)
            if feedback_json['result']:
                cookie_jar2.save(cookie_file, ignore_discard=True, ignore_expires=True)
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
            Get rsa2 encrypted password, using RSA module from https://pypi.python.org/pypi/rsa/3.1.1, documents can be accessed at
            http://stuvel.eu/files/python-rsa-doc/index.html
        """
        # n, n parameter of RSA public key, which is published by WEIBO.COM
        #hardcoded here but you can also find it from values return from prelogin status above
        #import pdb;pdb.set_trace()
        weibo_rsa_n = 'EB2A38568661887FA180BDDB5CABD5F21C7BFD59C090CB2D245A87AC253062882729293E5506350508E7F9AA3BB77F4333231490F915F6D63C55FE2F08A49B353F444AD3993CACC02DB784ABBB8E42A9B1BBFFFB38BE18D78E87A0E41B9B8F73A928EE0CCEE1F6739884B9777E4FE9E88A1BBE495927AC4A799B3181D6442443'

        #e, exponent parameter of RSA public key, WEIBO uses 0x10001, which is 65537 in Decimal
        weibo_rsa_e = 65537
        message = str(servertime) + '\t' + str(nonce) + '\n' + str(pwd)

        #construct WEIBO RSA Publickey using n and e above, note that n is a hex string
        key = rsa.PublicKey(int(weibo_rsa_n, 16), weibo_rsa_e)

        #get encrypted password
        if six.PY3:
            message = message.encode()
        encropy_pwd = rsa.encrypt(message, key)
        #trun back encrypted password binaries to hex string
        sp = binascii.b2a_hex(encropy_pwd)
        if six.PY3:
            sp = sp.decode('utf-8')
        return sp


    def get_user(self, username):
        import pdb;pdb.set_trace()
        username_ = urllib2.quote(username)
        if six.PY3:
            username = base64.encodestring(username_.encode())[:-1].decode('utf-8')
        if six.PY2:
            username = base64.encodestring(username_)[:-1]

        return username


class useAPI(object):
    def __init__(self):
        config = ConfigParser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), 'config.ini').replace('\\', '/'))
        self.APP_KEY = config.get('APPKEY', 'APP_KEY')
        self.APP_SECRET = config.get('APPKEY', 'APP_SECRET')
        self.CALLBACK_URL = config.get('APPKEY', 'CALLBACK_URL')
        self.token_file = os.path.join(os.path.dirname(__file__), 'token.pkl').replace('\\', '/')
        self.checked = self.check()

    def check(self):
        if os.path.isfile(self.token_file):
            try:
                token = pkl.load(open(self.token_file, 'r'))
                api = Client(self.APP_KEY, self.APP_SECRET, self.CALLBACK_URL, token)
                try:
                    api.get('statuses/user_timeline')
                    self.api = api
                    return True
                except:
                    print("token maybe out of time!")
            except:
                print("The token file error")
        return False

    def token(self, CODE=''):
        client, url = self.getCODE()
        if self.checked == False:
            if CODE == '':
                webbrowser.open_new(url)
                try:
                    # for python2.x
                    CODE = raw_input("Please Input the Code: ").strip()
                except:
                    # for python3.x
                    CODE = input("Please Input the Code: ").strip()
            try:
                client.set_code(CODE)
            except:
                print("Maybe wrong CODE")
                return
        token = client.token
        pkl.dump(token, open(str(self.token_file), 'wb'))
        self.api = Client(self.APP_KEY, self.APP_SECRET, self.CALLBACK_URL, token)
        self.checked = True

    def getCODE(self):
        client = Client(self.APP_KEY, self.APP_SECRET, self.CALLBACK_URL)
        return client, client.authorize_url

    def getURL(self):
        client = Client(self.APP_KEY, self.APP_SECRET, self.CALLBACK_URL)
        return client.authorize_url

    def get(self, url, count=1000, **kwargs):
        kwargs['count'] = count
        if self.checked == False:
            self.token()
        return self.api.get(url, **kwargs)

    def post(self, url, **kwargs):
        if self.checked == False:
            self.token()
        return self.api.post(url, **kwargs)


class simu(object):
    def __init__(self):
        config = ConfigParser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), 'config.ini').replace('\\', '/'))
        self.username = config.get('simu', 'username')
        self.password = config.get('simu', 'password')
        self.cookie_file = '/tmp/weibo_login_cookies.dat'
        self.simu = weibo_login(self.username, self.password)
        self.urls = []
        for k, v  in config.items('urls'):
            self.urls.append(v)
        self.webdata = {}

    @property
    def check_login(self):
        if not os.path.exists(self.cookie_file):
            print("weibo login is failer")
            return 1
        return 0

    @property
    def pre_weibo_login(self):
        if not os.path.exists(self.cookie_file):
            self.simu = weibo_login(self.username, self.password)

    def detail(self, url=None):
        if not url:
            url = self.urls

        if isinstance(url, str):
            self.webdata[url] = self._detail(url)

        if isinstance(url, list):
            for u in url:
                self.webdata[u] = self._detail(u)

        return self.webdata

    def _detail(self, url=None):
        if url:
            return jiexi(self.simu.getHTML(url))


def dataToUser(data):
    user = []
    for u in data:
        user.append(
            # {'text': 微博信息内容, 'count': 转发数, 'wid': 微博ID, 'name': 微博作者的用户信息字段, 'uid': 用户UID,
            # 'nick': 用户昵称, 'self': u['self'], 'timestamp': 微博创建时间, 'source': 微博来源,
            #  'location': 用户所在地, 'country_code': u['country_code'],
            #  'province_code': 用户所在省级ID, 'city_code': 用户所在城市ID, 'geo': 地理信息字段,
            #  'emotionurl': u['emotionurl'], 'emotiontype': u['emotiontype']
            # })
            {'text': u['text'], 'count': u['reposts_count'], 'wid': u['id'], 'name': u['user']['name'],
             'uid': u['user']['id'],
             'nick': u['user']['screen_name'], 'self': 'null',
             'timestamp': int(time.mktime(time.strptime(re.sub(r'\ \+\d+', '', str(u['created_at']))))),
             'source': u['source'],
             'location': u['user']['location'], 'country_code': '',
             'province_code': u['user']['province'], 'city_code': u['user']['city'], 'geo': u['geo'],
             # 'emotionurl': u['emotionurl'], 'emotiontype': u['emotiontype']
             'link': u['user']['id']
            })
    return user


def jiexi(content):
    import pdb;pdb.set_trace()
    if six.PY3:
        content = content.decode('utf-8')
    tmp = re.findall(r'pl\.content\.homeFeed\.index.*html\":\"(.*)\"}\)', content)
    # for tmp_r in tmp:
    # content = content.replace(tmp_r, 's')
    max = 0
    for i in tmp:
        if max < len(i):
            max = len(i)
            content = i

    content = content.replace('WB_detail', 'WB_detailWB_detail')

    # get all things
    WB_single = re.findall(r"WB\_detail(.+?)WB\_detail", content)
    # for i in range(0,len(WB_single)):
    # {'text': 微博信息内容, 'count': 转发数, 'wid': 微博ID, 'name': 微博作者的用户信息字段, 'uid': 用户UID,
    #  'nick': 用户昵称, 'self': u['self'], 'timestamp': 微博创建时间, 'source': 微博来源,
    #  'location': 用户所在地, 'country_code': u['country_code'],
    #  'province_code': 用户所在省级ID, 'city_code': 用户所在城市ID, 'geo': 地理信息字段,
    #  'emotionurl': u['emotionurl'], 'emotiontype': u['emotiontype']
    # })
    # {'text': u['text'], 'count': u['reposts_count'], 'wid': u['id'], 'name': u['user']['name'],
    #  'uid': u['user']['id'],
    #  'nick': u['user']['screen_name'], 'self': 'null', 'timestamp': u['created_at'], 'source': u['source'],
    #  'location': u['user']['location'], 'country_code': '',
    #  'province_code': u['user']['province'], 'city_code': u['user']['city'], 'geo': u['geo'],
    #  # 'emotionurl': u['emotionurl'], 'emotiontype': u['emotiontype']
    #  'link': u['user']['id']
    # })
    user = []
    for WB in WB_single:
        # 正文
        #import pdb;pdb.set_trace()
        WB_text = ''.join(re.findall(r"WB\_text[^>]*>(.*?)<\\/div", WB)).replace('\\n', '').replace('\\"', '"').replace('\\/', '/').strip()  #.lstrip('\\n').strip()

        # if WB_text inclued WB_media_expand is miniPage !!!!!!
        #WB_source = ''.join(re.findall(r'WB\_text[^>]*>.*nofollow\\">(.*?)<', WB))  # checked

        # 图片收集
        #import pdb;pdb.set_trace()
        #reg = r'src="(.*?\.jpg)"'
        #WB_img = ''.join(re.findall(r'src=.*.sinaimg.cn.*.jpg', WB))

        # 收藏
        #WB_favorite = re.findall(r'ficon\_favorite[^>]*>(.)<\\/em><em>(\w+)<\\/em>', WB)[-1][-1] #checked
        #WB_favorite = re.findall(r'收藏|已收藏', WB)  # checked

        # 转发
        #WB_forward = re.findall(r'<em>(\d+)<\\/em>', WB)[0] #checked

        # 评论
        #WB_repeat = re.findall(r'<em>(\d+)<\\/em>', WB)[1] #checked
        #WB_repeat = re.findall(r'ficon\_repeat[^>]*>(&#xe\d+;)<\\/em><em>(\d+)<\\/em>', WB)[-1][-1] #checked

        # 点赞
        #WB_praised = re.findall(r'<em>(\d+)<\\/em>', WB)[2] #checked

        WB_like = ''.join(re.findall(r'WB\_text[^>]*>.*praised.*?\(([0-9]*)', WB))  # checked
        WB_mid = re.findall(r'mid=.*?(\d*)', WB)[-1]  # checked
        WB_name = ''.join(re.findall(r'nick-name=\\"([^"]*)\\"', WB))
        WB_uid = ''.join(re.findall(r'fuid=([^"]*)\\"', WB))  # checked
        WB_timestamp = re.findall(r'date=\\"([^"]*)\\"', WB)[-1]  # checked

        dateArray = datetime.datetime.utcfromtimestamp(int(WB_timestamp) / 1000)
        otherStyleTime = dateArray.strftime("%Y-%m-%d %H:%M:%S")

        user.append({
            'text': WB_text,
            #'source': WB_source,
            #'收藏': WB_favorite,
            #'转发': WB_forward,
            #'评论': WB_repeat,
            #'点赞': WB_praised,
            'time': otherStyleTime,
            'mid': WB_mid,
            'name': WB_name,
            'uid': WB_uid,
            'nick': WB_name,
            'self': 'dontknow', 'location': 'null', 'country_code': '', 'province_code': 'null',
            'city_code': 'null',
            'geo': 'null',
            'link': WB_uid,
            'like': WB_like,
        })

    return user, len(user)

def getImg(url, mid):
    pass

mids = []
maxcount = 4
def get_all_mid(api, max_id=0, count=100, page=0, base_app=0, feature=0):
    global mids
    global maxcount
    import pdb;pdb.set_trace()
    morepage = api.get('statuses/friends_timeline/ids', 100, page=1)
    next_cursor = morepage.get('next_cursor')
    mids.extend(morepage.get('statuses'))
    maxcount = maxcount - 1

    if not int(next_cursor) or not maxcount:
        mids = list(set(mids))
    else:
        get_all_mid(api, int(next_cursor))

    return 0


def get_one_mid(api, id, page=0, base_app=0, feature=0):
    import pdb;pdb.set_trace()
    morepage = api.get('statuses/friends_timeline',
                       2,
                       since_id=0,
                       max_id=id,
                       page=1)
    print morepage.get('statuses')

if __name__ == '__main__':
    # api = useAPI()
    # print(api.get('statuses/user_timeline'))
    # config = ConfigParser.ConfigParser()
    # config.read(os.path.join(os.path.dirname(__file__), 'config.ini').replace('\\', '/'))
    # username = config.get('simu', 'username')
    # pwd = config.get('simu', 'pwd')
    # html = weibo_login(username, pwd)
    # print(html.getHTML('http://www.weibo.com/kaifulee'))
    import pdb
    #pdb.set_trace()
    #aa = simu()
    #aa.pre_weibo_login
    #print(aa.detail('http://weibo.com/kaifulee'))
    #wburl = "http://weibo.com/u/3538755522?is_all=1#1464674122618"
    #print(aa.detail(wburl))

    # API 参考 http://open.weibo.com/wiki/%E5%BE%AE%E5%8D%9AAPI
    # 使用参考 https://github.com/lxyu/weibo
    api = useAPI()
    #print(api.get('statuses/user_timeline', 200, uid=3538755522))
    #print(api.get('account/get_uid'))
    #print(get_all_mid(api))
    #print mids
    #get_one_mid(api, 3979151650306475)

    #morepage = api.get('statuses/friends_timeline/ids', 100, page=1, max_id=3976020019056463)
    #print(morepage.get('next_cursor'))
    #print(morepage.get('statuses'))
    #print(api.get('comments/show', 2,id=3981153851194444))
    #print(api.get('statuses/user_timeline/ids', uid=3538755522))
    #print(api.get('statuses/queryid', mid="1035051413304027"))
    #ujson = api.get('statuses/show_batch', ids="3538755522")
    #ujson = api.get('users/show', screen_name="海涛法师")
    #print ujson.get('profile_url')
    ujson = api.get('users/show', screen_name="圆善法师")
    #ujson = api.get('statuses/querymid', id=3538755522, type=2, is_batch=1)
    print(ujson)
    #ujson = api.get('users/counts', uids=1337970873)#    print(ujson)
    # print(api.post('statuses/update', status='test from my api'))
