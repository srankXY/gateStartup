# gateStartup

## 功能

> - 自动登录gate.io
> - 自动认购gateStartup打新
> - 保存一定时间的gate.io session
> - **无法提现，无法交易**

## 部署

### 环境

> **python**：`3.9+`
>
> **库**：`selenium`，`configparser`，`requests`，`python_authentiator`

### 安装

```shell
pip install -r requirements.txt
```

### 运行

```shell
python3.9 gateStartup.py
```

## 配置

```ini
# 仅支持手机号码 + 密码登录
[gate]
url = https://www.gate.io/zh
username = 
password = 
country = 中国
google_secret = 			# 2FA密钥

# 用户滑动验证码过检
[cjy]
cjyUser = 
cjyPassword = 
softId = 

[proxy]
# 0关闭，1开启
enable = 0
addr = 127.0.0.1:7890

[main]
# 多久刷新一次startup，单位h
cron = 1
# 滑块验证码重试次数
retries = 5
```

