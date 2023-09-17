# SummaryCard 摘要卡
from Jce import JceInputStream, JceStruct
from Jce_b import JceWriter, JceReader

from AndroidQQ.package import PackHeadNoToken, Pack_, Un_jce_Head


def ReqSummaryCard(info, **kwargs):
    """需求摘要卡
    package SummaryCard;
    """

    def vReqLastGameInfo():
        """获取最后一次游戏信息"""
        pass

    Uin = int(kwargs.get('Uin', 0)) or int(info.uin)

    jce = JceWriter()
    jce.write_int64(Uin, 0)
    jce.write_int64(1, 1)  # eComeFrom 来自
    jce.write_int64(0, 2)  # uQzoneFeedTimestamp QQ空间动态发送时间
    jce.write_bool(kwargs.get('bIsFriend', True), 3)  # 是否是好友 不是好友也能发成好友
    jce.write_int64(kwargs.get('lGroupCode', 0), 4)  # 群组 来源ID
    jce.write_int64(kwargs.get('lGroupUin', 0), 5)  # 群组
    jce.write_bytes(bytes.fromhex('00'), 6)  # cache_vSeed
    jce.write_string(kwargs.get('strSearchName', ''), 7)  # 搜索的名称
    jce.write_int64(kwargs.get('lGetControl', 69181), 8)  #
    jce.write_int32(kwargs.get('eAddFriendSource', 10004), 9)  # 添加好友来源
    jce.write_bytes(bytes.fromhex('00'), 10)  # vSecureSig 安全签名
    # jce.write_bytes(kwargs.get('cache_vReqLastGameInfo', 0), 12)  # 缓存 v 请求上次游戏信息
    # todo 暂时不处理其他信息

    _data = jce.bytes()
    # print(_data.hex())
    _data = JceWriter().write_jce_struct(_data, 0)

    # _data = JceWriter().write_map({'ReqSummaryCard': {'SummaryCard.ReqSummaryCard': _data},
    #                                'ReqHead': {'SummaryCard.ReqHead': bytes.fromhex('0A 00 02 0B')}}, 0)
    #
    _data = JceWriter().write_map({'ReqHead': bytes.fromhex('0A 00 02 0B'), 'ReqSummaryCard': _data},
                                  0)  # 似乎新版有更多的验证,因此用旧的头部

    _data = PackHeadNoToken(info, _data, 'SummaryCard.ReqSummaryCard',
                            'SummaryCardServantObj', 'ReqSummaryCard')
    _data = Pack_(info, _data, Types=11, encryption=1, sso_seq=info.seq)

    return _data


def ReqSummaryCard_res(data):
    """需求摘要卡"""
    data = Un_jce_Head(data)
    _map = JceReader(data).read_map(0)
    _dict = _map.get('RespSummaryCard', None)
    # print(_dict)
    if _dict:
        RespSummaryCard = _dict['SummaryCard.RespSummaryCard']
        stream = JceInputStream(RespSummaryCard)
        jce = JceStruct()
        jce.read_from(stream)
        return jce.to_json()
    else:
        return None
