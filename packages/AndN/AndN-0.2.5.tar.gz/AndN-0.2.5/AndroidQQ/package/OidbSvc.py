import json
# 对象数据服务
from google.protobuf.json_format import MessageToJson, MessageToDict

from AndroidQQ.proto import *
from AndroidQQ.package.head import *
from pyproto import ProtoBuf


def P_0xeb8(info):
    """	 uint32_src = 1 proto_ver = 2  {1: 1, 2: 2} 	"""

    _dict = {1: 3768, 2: 1, 4: {1: 1, 2: 2}}
    _data = ProtoBuf(_dict).toBuf()
    _data = PackHeadNoToken(info, _data, 'OidbSvc.0xeb8')
    _data = Pack_(info, _data, Types=11, encryption=1, sso_seq=info.seq)
    return _data


def P_0xeb8_res(data):
    """返回绑定手机信息"""
    new_msg = OidbSvc0xeb8r()
    new_msg.ParseFromString(data)
    return MessageToDict(new_msg)['RspBody']


def P_0x88d_1(info):
    msg = OidbSvc0x88d1()
    msg.field1 = 2189
    msg.field2 = 1
    msg.field4.field1 = 537046294
    msg.field4.field2.field1 = 799854399
    msg.field4.field2.field2.field7 = 0
    msg.field4.field2.field2.field24 = b''  # Replace this with your intended byte array
    # 序列化消息
    bytes_temp = msg.SerializeToString()
    bytes_temp = Pack_Head(info, bytes_temp, 'OidbSvc.0x88d_1')
    bytes_temp = Pack_(info, bytes_temp, Types=8, encryption=1, token=True)
    return bytes_temp


def P_0x88d_1_res(data):
    """返回字典"""
    new_msg = OidbSvc0x88d1r()
    new_msg.ParseFromString(data)
    return MessageToDict(new_msg)


def P_0xc05(info, **kwargs):
    """获取授权列表"""
    _dict = {1: 3077, 2: 1, 3: 0, 4: {11: {1: kwargs.get('start', 0), 2: kwargs.get('limit', 10)}}}
    _data = ProtoBuf(_dict).toBuf()
    _data = PackHeadNoToken(info, _data, 'OidbSvc.0xc05')
    _data = Pack_(info, _data, Types=11, encryption=1, sso_seq=info.seq)
    return _data


def P_0xc05_res(data):
    """返回字典"""
    new_msg = OidbSvc0xc05r()
    new_msg.ParseFromString(data)
    return MessageToDict(new_msg)['RspBody']['AppListRsp']


def P0xccd(info, **kwargs):
    """删除授权信息"""
    _dict = {1: 3277, 2: 1, 3: 0, 4: {2: kwargs.get('appid', 0), 3: 1}}
    _data = ProtoBuf(_dict).toBuf()
    _data = PackHeadNoToken(info, _data, 'OidbSvc.0xccd')
    _data = Pack_(info, _data, Types=11, encryption=1, sso_seq=info.seq)
    return _data


def P0xccd_res(data):
    _dict = ProtoBuf(data).toDictAuto()
    return _dict
