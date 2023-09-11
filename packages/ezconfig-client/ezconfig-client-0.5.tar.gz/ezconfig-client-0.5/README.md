# EZConfig 客户端程序

## 使用方法

```text
pip install ezconfig-client
```

```python
from ezconfig_client import loader
res = loader.get_latest_config()
print(res)
```

使用前需要设置环境变量

| 环境变量 | 说明 |
| --- | --- |
| EZCONFIG_ENV | 环境变量 |
| EZCONFIG_APPID | 应用ID |
| EZCONFIG_SECRET | 应用密钥 |
| EZCONFIG_HOST | EZConfig服务地址 |


环境依赖：

```text
requests>=2.22.0
retrying>=1.3.4
```

**测试参考代码**

EZCONFIG_ENV=DEV EZCONFIG_APPID=xxx.xx.xxx EZCONFIG_SECRET=xxxxxxx EZCONFIG_HOST=https://xxxx.xx python test/test.py

## 版本说明

| 版本  | 变更                        |
|-----|---------------------------|
| 0.4 | 降低requests版本，修改bug        |
| 0.5 | 增加访问错误重试机制，请求超时30秒，失败重试3次 |

