# 91Crawer

这个项目是抓取91Porn网站上的“10分钟以上”标签的视频

[![Build Status](https://travis-ci.org/lizhaode/91Crawer.svg?branch=master)](https://travis-ci.org/lizhaode/91Crawer)

### 使用方法

#### 环境配置

    关于GFW没有做任何处理，所以最好是在国外的VPS上执行。目前在Ubuntu 16.04LTS + Python3.5上验证通过,没有做Python2兼容，请使用Python3。
    
    如果你想在本地执行，首先翻墙，然后在Pycharm中配置好代理，执行亦可
    
#### 使用步骤

    git clone 项目后，使用 `pip install -r requirements.txt`安装依赖，然后执行 `python3 main.py` 即可
 
 #### 程序大体逻辑
 
 1. 解析网页，获取视频的名称和播放视频的页面 url
 2. 将解析结果写入数据库(SQLite)
 3. 从数据库中读取一条一条的数据，解析真实的视频地址
 4. 使用 aria2 下载
 5. 下载完毕，更新这条的数据库状态
 
 
 #### 多线程改造计划
 
 - [x] 即时解析下载
 - [ ] 使用数据库存储解析和下载情况
