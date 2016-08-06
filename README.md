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
yum install -y gcc mysql-devel python-devel
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
2.1. 配置mysql 数据库
[client]
default-character-set=utf8

[mysql]
default-character-set=utf8


[mysqld]
collation-server = utf8_unicode_ci
init-connect='SET NAMES utf8'
character-set-server = utf8

2.2 创建数据库
 create database weibo DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

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
1, 执行命令

这个时候会出现 以下提示信息 并且会打开默认浏览器
浏览器中的url 类似 http://127.0.0.1/?code=4a1291079a25335c12d0c39eef6c5a5b
要复制 code 后的 信息 如: 4a1291079a25335c12d0c39eef6c5a5b
然后在 粘贴 到 如下的提示信息中 然后 回车

Please Input the Code: Created new window in existing browser session.
4a1291079a25335c12d0c39eef6c5a5b


weibapi --config-file etc/weibo.conf


```

定时更新微博信息
====
```
周期性的获取数据信息
# 由于 weibo 官网 api  有次数限制 userdata 数据 一小时 更新一次。
# weibo 大号的信息 每5 分钟更新一次
weibo --config-file etc/weibo.conf
```

后台运行程序
====
```
weibo &>/dev/null &
```

设置开机启动
====
```
前提， centos7 操作系统
cp etc/weibo.service /usr/lib/systemd/system/
systemctl enable weibo.service
systemctl start weibo.service
```



全新安装与介绍
===
```
```

