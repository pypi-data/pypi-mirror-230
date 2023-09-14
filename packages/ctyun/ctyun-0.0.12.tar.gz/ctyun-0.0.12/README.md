

### Summary

This package is to quickly generate inventory report for your cloud resources located on https://www.ctyun.cn.


### Credentials
To get your correct accessKey and secretKey, You need contact your service manager.
Credential file needs to be placed at '~/.ctyun/credential' as:
```text

[default]
accesskey=your_own_access_key
secretkey=your_own_secret_key

```
### Usage

```python
from ctyun import inventory
_v = inventory(regionId='cn-bj1', api='getVpcs')
_v.json

```

