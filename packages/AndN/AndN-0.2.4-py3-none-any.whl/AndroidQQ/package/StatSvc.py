import json
import zlib

from Jce import JceInputStream, JceStruct

from AndroidQQ.package.head import *


# 统计服务
def GetDevLoginInfo(info, **kwargs):
    """获取登录信息"""
    jce = JceWriter()
    jce.write_bytes(info.Guid, 0)
    jce.write_string('com.tencent.mobileqq', 1)
    jce.write_int32(1, 2)
    jce.write_int32(0, 3)
    jce.write_int32(0, 4)
    jce.write_int32(20, 5)
    jce.write_int32(kwargs.get('type', 3), 6)
    _data = jce.bytes()

    _data = JceWriter().write_jce_struct(_data, 0)
    _data = JceWriter().write_map({'SvcReqGetDevLoginInfo': _data}, 0)

    _data = PackHeadNoToken(info, _data, 'StatSvc.GetDevLoginInfo', 'StatSvc', 'SvcReqGetDevLoginInfo')
    _data = Pack_(info, _data, Types=11, encryption=1, sso_seq=info.seq)
    return _data


def GetDevLoginInfo_res(data):
    if data[0] == 120:
        data = zlib.decompress(data)
    data = Un_jce_Head(data)
    data = Un_jce_Head_2(data)
    stream = JceInputStream(data)
    s = JceStruct()
    s.read_from(stream)
    return s.to_json()


def DelDevLoginInfo(info, **kwargs):
    """删除登录信息"""
    key = kwargs.get('key', b'')
    if isinstance(key, str):
        key = bytes.fromhex(key)

    _data = JceWriter().write_bytes(key, 0)

    jce = JceWriter()
    jce.write_bytes(info.Guid, 0)
    jce.write_string('com.tencent.mobileqq', 1)
    jce.write_jce_struct_list([_data], 2)
    jce.write_int32(1, 3)
    jce.write_int32(0, 4)
    jce.write_int32(0, 5)
    _data = jce.bytes()
    _data = JceWriter().write_jce_struct(_data, 0)
    _data = JceWriter().write_map({'SvcReqDelLoginInfo': _data}, 0)
    _data = PackHeadNoToken(info, _data, 'StatSvc.DelDevLoginInfo', 'StatSvc', 'SvcReqDelLoginInfo')
    _data = Pack_(info, _data, Types=11, encryption=1, sso_seq=info.seq)
    return _data


def DelDevLoginInfo_res(data):
    """似乎没有明确的返回信息"""
    data = Un_jce_Head(data)
    data = Un_jce_Head_2(data)
    stream = JceInputStream(data)
    jce = JceStruct()
    jce.read_from(stream)
    return jce.to_json()


def register(info, **kwargs):
    """登录注册"""
    jce = JceWriter()
    jce.write_int64(int(info.uin), 0)
    jce.write_int32(kwargs.get('bid', 7), 1)  # login: 1 | 2 | 4 = 7, 登出: 0.
    jce.write_int32(0, 2)  # 连接类型
    jce.write_string('', 3)  # 其他
    jce.write_int32(kwargs.get('online_status', 11), 4)  # 在线状态 线上: 11, 离线: 21
    jce.write_bool(False, 5)  # 在线推送
    jce.write_bool(False, 6)  # 在线
    jce.write_bool(False, 7)  # 正在显示在线
    jce.write_bool(False, 8)  # 踢电脑
    jce.write_bool(False, 9)  # 踢弱
    jce.write_int64(0, 10)  # 时间戳
    jce.write_int64(25, 11)  # ios_version
    jce.write_int64(1, 12)  # 网络类型
    jce.write_string('', 13)  # 构建版本
    jce.write_int32(0, 14)
    jce.write_bytes(info.Guid, 16)
    jce.write_int16(2052, 17)  # 区域设置 ID
    jce.write_int32(0, 18)  # 无声推动
    jce.write_string('', 19)  # 开发者名称
    jce.write_string('', 20)  # 开发类型
    jce.write_string('7.1.2', 21)  # os_version
    jce.write_int32(1, 22)  # 打开推送
    jce.write_int64(41, 23)  # 大序列
    jce.write_int64(0, 24)  # 最后观看开始时间
    jce.write_int64(0, 26)  # 旧单点登录 IP
    jce.write_int64(0, 27)  # 新的单点登录 IP
    _data = jce.bytes()
    jce = JceWriter()
    jce.write_jce_struct(_data, 0)
    _data = jce.bytes()

    jce = JceWriter()
    jce.write_map({'SvcReqRegister': _data}, 0)
    _data = jce.bytes()

    jce = JceWriter()
    jce.write_int32(3, 1)
    jce.write_int32(0, 2)
    jce.write_int32(0, 3)
    jce.write_int64(0, 4)
    jce.write_string('PushService', 5)
    jce.write_string('SvcReqRegister', 6)
    jce.write_bytes(_data, 7)
    jce.write_int32(0, 8)
    _data = jce.bytes()
    _data = _data + bytes.fromhex('98 0C A8 0C')  # 后面的两个空的
    _data = Pack_Head(info, _data, 'StatSvc.register')
    _data = Pack_(info, _data, Types=10, encryption=1, token=True)
    return _data


def register_res(data):
    data = Un_jce_Head(data)
    data = Un_jce_Head_2(data)
    stream = JceInputStream(data)
    s = JceStruct()
    s.read_from(stream)
    return s.to_json()
