# Alist-API-V3

根据[Alist API V3文档](https://alist.nn.ci/zh/guide/api/)，使用Python3实现的异步Alist V3 API SDK

! 注意: 本SDK未经严格测试，请勿轻易用于生产环境

## 安装

```bash
pip install alist_v3
```

## 使用

```python
import asyncio
from alist_v3 import AsyncClient


async def main():
    async with AsyncClient(usr='ur_user_name', pwd='ur_password', url="http://ur_url.com") as client:
        msg = await client.get_me()
        print(msg)
        print(await client.post_mkdir('/aliyun/test'))
        print(await client.post_list('/aliyun')) 

if __name__ == '__main__':
    asyncio.run(main())
```

## API

本SDK的Method与[Alist文档](https://alist.nn.ci/zh/guide/api/)中的API名称接近一致，可以参考文档使用

如有问题，可提issue