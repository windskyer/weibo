weibo
====
微博爬虫软件, 给定指定的 微博大号，获取所有的 微博信息

usage
===

```
1, 修改配置文件 config.ini 
[simu]
# 设置微信的 账户
username = 
# 设置微信的 账户密码
password = 


设置所有要 爬虫的 url
[urls]

#延参法师
url1 = http://weibo.com/hutuheshang

#学诚法师
url2 = http://weibo.com/xuecheng

#济群法师
url3 = http://weibo.com/jiqun
```


运行环境 安装方法
====
```
支持超在系统 centos7 , fedora21, centos6.x

支持 python2.x
#python2 run.py

不支持 python3.x
#python3 run.py

安装方法
pip install -r requirements.txt
python setup.py install

```

database
====
```
1, 设置 配置文件中的sql 地址
[database]
sql_connection = mysql://weibo:weibo@192.168.122.206/weibo?charset=utf8

2, 在mysql数据库 中的 创建 weibo 数据库
create database weibo;

3, 同步数据库表格
weibodb --config-file etc/weibo.conf
```

获取数据
====
```
1, 执行获取命令
weibopc --config-file etc/weibo.conf
```

获取用户信息
====
```
weibapi --config-file etc/weibo.conf
```

