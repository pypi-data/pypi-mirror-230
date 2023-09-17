# MQ更新服务_com_qq_ti
import json

from google.protobuf.json_format import MessageToJson

from AndroidQQ.package.head import PackHeadNoToken, Pack_
from AndroidQQ.proto import *


def web_scan_login(info, **kwargs):
    """
    扫描登录
    :param info:
    :param kwargs:
        uint32_service_type int 4 扫码 5 确认登录
        bytes_token str
    :return:
    """
    # 扫描登录
    msg = web_scanlogin()
    msg.field2 = 0
    msg.field3 = json.dumps(kwargs).encode('utf-8')  # 这个参数是json
    _data = msg.SerializeToString()
    _data = PackHeadNoToken(info, _data, 'MQUpdateSvc_com_qq_ti.web.scanlogin')
    _data = Pack_(info, _data, Types=11, encryption=1, sso_seq=info.seq)
    return _data


def web_scan_login_res(data):
    msg = web_scanlogin_res()
    msg.ParseFromString(data)
    return msg.field4.decode()
