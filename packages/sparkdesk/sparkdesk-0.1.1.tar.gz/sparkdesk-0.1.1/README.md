# sparkdesk 讯飞星火大模型api

## 安装

TODO ...

## 讯飞星火 API 申请

讯飞星火的API需要前往官网进行[申请](https://xinghuo.xfyun.cn/sparkapi?scr=price)。
新用户可获取一定量都免费额度。

## CLI 使用方法

```shell
> python -m sparkdesk.cli --help
Usage: python -m sparkdesk.cli [OPTIONS]

Options:
  --app-id TEXT      [required]
  --api-secret TEXT  [required]
  --api-key TEXT     [required]
  --help             Show this message and exit.
```

## API使用方法

参考： `sparkdesk/cli.py`
接口返回数据结构参考官方文档 https://www.xfyun.cn/doc/spark/Web.html

## TODO

1. 添加 async API
2. 添加返回JSON数据对应的 dataclass
