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
==
数据库表结构介绍
===
```
userdata 表
    # 用户id
    uid = Column(BigInteger)
    
    # 昵称
    screen_name = Column(String(64))
    
    # 友好名称
    name = Column(String(32))
    
    # 用户所在地方
    location = Column(String(64))
    
    # 简介
    description = Column(String(200))
    
    # 关注数量
    friends_count = Column(BigInteger)
    
    # 粉丝数量
    followers_count = Column(BigInteger)
    
    # 标签
    ability_tags = Column(String(15))
    
    # 性别
    gender = Column(String(15), default='m')

    # 等级
    urank = Column(Integer, default=0)

    # 阳光信用
    credit_score = Column(Integer, default=0)

    # 注册时间
    created_at = Column(DateTime)
    
    # 主页地址
    profile_url = Column(String(150))

    # 微博主页地址
    homepage = Column(String(150)) 

    # 头像
    profile_image_url = Column(String(150), default=None)

    # 出生日期
    birthdate = Column('birthdate', String(200))

    # 认证原因
    verified_reason = Column('verified_reason', String(200))

    # 是否认证
    verified = Column('verified', Boolean, default=False)

    # 个人备注， 个性签名
    remark = Column('remark', String(200))

weibo 表（微博的描述信息）
    # 微博id
    mid = Column(BigInteger, nullable=False)
    
    # user id
    uid = Column(BigInteger, nullable=False)
    
    # 转发数量
    forward = Column(BigInteger)
    
    # 评论数量
    repeat = Column(BigInteger)
    
    # 点赞数量
    praised = Column(BigInteger)
    
    # 发布时间
    time_at = Column(String(150))
    datetime_at = Column(DateTime)
    
    # 发布来源
    source = Column(String(150))

zfwbimg(转发微博的 图片地址)
    
    # 微博mid
    mid = Column(BigInteger, nullable=False)
    
    # 用户UID
    uid = Column(BigInteger, nullable=False)
    
    # img所在地方
    location = Column(String(200))
    
    # img 的 url 地址
    url = Column(String(200))
    
    # big img 的 url 地址
    bigurl = Column(String(200))
    
    # 是否是转发微博
    is_zf = Column(Boolean, default=False)
    
    # 转发微博的mid
    pa_mid = Column(BigInteger, nullable=True)

wbimg（微博 图片地址）
    # 微博mid
    mid = Column(BigInteger, nullable=False)

    # 用户UID
    uid = Column(BigInteger, nullable=False)
    
    # img所在地方
    location = Column(String(200))
    
    # img 的 url 地址
    url = Column(String(200))
    
    # big img 的 url 地址
    bigurl = Column(String(200))
    
    # 是否是转发微博
    is_zf = Column(Boolean, default=False)
    
    # 被转发weibo 的mid
    zf_mid = Column(BigInteger, nullable=True)
    
 wbtext 表  （微博的类容信息）
    # 微博mid
    mid = Column(BigInteger, nullable=False)
    
    # 用户UID
    uid = Column(BigInteger, nullable=False)

    # text info
    text = Column(Text)
    
    # face 表情 info
    face = Column(Text)
    
    # 文本中的link 的 url 地址
    url = Column(Text)
    
    # 是否是转发微博
    is_zf = Column(Boolean, default=False)
    
    # 转发weibo 的mid
    zf_mid = Column(BigInteger, nullable=True)
    
 zfwbtext 表 （转发 微博的 类容信息）
    # 微博mid
    mid = Column(BigInteger, nullable=False)
    
    # 用户UID
    uid = Column(BigInteger, nullable=False)

    # text info
    text = Column(Text)
    
    # face 表情 info
    face = Column(Text)
    
    # 文本中的link 的 url 地址
    url = Column(Text)
    
    # 是否是转发微博
    is_zf = Column(Boolean, default=False)
    
    # 被转发weibo 的mid
    pa_mid = Column(BigInteger, nullable=True)
```
安装方法
===
```
1, 下载
git clone https://github.com/windskyer/weibo.git
或者
wget -c https://github.com/windskyer/weibo/archive/2016.7.11.tar.gz (选择合适版本)

2， 安装
cd weibo
pip install -r requirements.txt   (如果出错  打开 requirements.txt 文件查看解决方法)
python setup.py install

3, 修改配置文件
安装完成后  在 /etc/weibo/weibo.conf 配置中做修改(根据需要自行修改过)
设置 配置文件中的sql 地址
[database]
sql_connection = mysql://weibo:weibo@192.168.122.206/weibo?charset=utf8

安装完成后  在 /etc/weibo/user.json 文件中 设置 需要爬虫的 weibo 大号
{
        "nickname": "延参法师",
        "url": "",
        "delete": "False"
 },
 文件以一个 dict 为单位  如上  添加 延参法师 的微博
 注意： 设置 delete 为 True 时候  表示 是 不在爬虫这个 微博大号 默认是 False
 修改 user.json  不需重启服务， 动态添加和删除微博大号
 
 
 4，同步数据库
 安装完成后， 和  配置修改过完成后.
 create database weibo DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; #创建数据库
 weibodb   #同步数据库
 
 
 5， 运行服务
 
 安装完成后， 和  配置修改过完成后， 运行服务。
 运行服务有两种方式
 
   一， 运行命令  weibo &>/dev/null &  开启微博服务。 
   
   二,  如果需要快速 更新数据库中数据则 运行如下命令
         weiboapi   可以根据配置为weibo.conf 中的 enable_multitargets = t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t13, t12, t14, t15, t16, t17, t18, t19, t20  项 来快速更新 userdata 表中数据
         
         weibopc  开始更新 weibo 信息到数据。
         
         weibodn  开始下载 weibo 中的img 图片到本地



