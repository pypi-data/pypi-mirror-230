crew member sentry notification plugin
===

机组使用的[sentry-onpremise](https://github.com/getsentry/onpremise)使用的通知插件

目前包含了

+ 企业微信
+ 钉钉

两种通知方式

底层基于群聊机器人的webhook

sentry测试版本：`23.3.1`

安装方法：

进入sentry目录

1. `vim enhance-image.sh`

添加下面内容

```bash
pip install csnp==0.0.6
```

2. 构建并重启sentry


`sudo docker-compose down`

`sudo ./install.sh`

`sudo docker-compose up -d`
