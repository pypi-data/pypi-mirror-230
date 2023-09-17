# 登录相关
import time

from AndTools import pack_b, TEA, pack_u

from AndroidQQ.package.Tlv import TLV
from AndroidQQ.package.Tlv_res import Un_Tlv
from AndroidQQ.package.head import Pack_Head_login, Pack_, Pack_Head_login_test


def login(info, **kwargs):
    """登录包"""
    info.uin = kwargs['uin']
    info.password = kwargs['password']
    info.Guid = kwargs.get('Guid', None)
    if not info.Guid:
        info.Guid = bytes.fromhex('69 4C 16 6C BA 92 7C CD C5 32 73 13 79 FF 74 DA')

    print('GUid', info.Guid.hex())
    _tlv = TLV(info)
    pack = pack_b()
    if info.device.client_type == 'Watch':
        # 手表协议
        methods = [
            _tlv.T018(),
            _tlv.T001(),
            _tlv.T106(),  # 必须
            _tlv.T116(),  # 必须
            _tlv.T100(5, 16, 0, 33820864),  # 必须
            _tlv.T107(),  # 必须
            _tlv.T142(),  # 必须
            _tlv.T144(),  # 必须
            _tlv.T145(),  # 必须
            _tlv.T147(),
            _tlv.T16A(),  # 必须
            _tlv.T154(),
            _tlv.T141(),
            _tlv.T008(),
            _tlv.T187(),
            _tlv.T188(),
            _tlv.T194(),
            _tlv.T191('00'),
            _tlv.T202(),
            _tlv.T177(),
            _tlv.T516(),
            _tlv.T521(115),
            _tlv.T318(),  # s
            # _tlv.T544
        ]
    elif info.device.client_type == 'Tim':
        info.key_Pubkey = bytes.fromhex(
            '04 56 F1 AC E7 71 73 EF F2 6C 31 4E 12 3F 6E A0 5B D1 7C 37 DF 3F 61 80 2C 51 F8 5B C3 69 C2 48 DB 1C 72 1C 38 08 8A 59 2E 99 94 92 C6 0F 9E 9E 45 D9 58 37 AE 2E D0 10 FD 32 8D 58 29 E8 39 F6 E3')  #
        info.share_key = bytes.fromhex('5B9EFFCD3C54E9FBBE7560A0290CE076')
        info.key_rand = bytes.fromhex('99375BA2B9AF634B0D6532C118ADF33C')
        info.key_tg = bytes.fromhex('F4 67 85 E9 38 85 5F FF 71 41 B7 88 E2 28 B9 9D')
        info.Guid = bytes.fromhex('9b6be0653a356f4fac89926f3f1ceb7e')
        info.uin = kwargs['uin']
        info.password = kwargs['password']
        methods = []
    elif info.device.client_type == 'QQ_old':


        # info.key_Pubkey = bytes.fromhex(
        #     '04 48 83 C6 0D 32 82 3D 7C 5B 05 80 16 8B 4B 6A 56 46 E3 78 2B 6D C6 82 9D 5D 36 10 BD AF 07 60 DC 31 AF 8C A4 BC C5 B2 B2 82 69 3C F8 90 C2 13 31 28 9F FF 12 3A 84 16 D1 3A 36 CA 59 04 26 96 F3')  #
        # info.share_key = bytes.fromhex('D8 5A 46 FF E3 6C 56 2C 8A 3A 4E E7 AF B2 25 77')
        # info.key_rand = bytes.fromhex('B6153247AA194EB9991CBDCE4A4C234C')
        # info.key_tgtgt = bytes.fromhex('B6 15 32 47 AA 19 4E B9 99 1C BD CE 4A 4C 23 4C')

        methods = [
            _tlv.T018(),
            _tlv.T001(),
            _tlv.T106(),  # 必须
            _tlv.T116(),  # 必须
            _tlv.T100(15, 16, 0, 34869472),  # 必须
            _tlv.T107(),  # 必须
            _tlv.T142(),  # 必须
            _tlv.T144(),  # 必须
            _tlv.T145(),  # 必须
            _tlv.T147(),
            _tlv.T154(),
            _tlv.T141(),
            _tlv.T008(),
            _tlv.T511(),
            _tlv.T187(),
            _tlv.T188(),
            _tlv.T191('82'),
            _tlv.T202(),
            _tlv.T177(),
            _tlv.T516(),
            _tlv.T521(0),
            _tlv.T525('00 01 05 36 00 02 01 00'),
            # _tlv.T544(),
            # _tlv.T545(),
            # _tlv.T548(),

        ]


    else:
        # 默认普通QQ
        info.key_Pubkey = bytes.fromhex(
            '04 6F 9E D9 8C FB 8B 92 73 73 69 6E B7 CA 40 A5 BE 28 84 D0 EF EC D5 96 84 C2 E9 14 50 8F A9 7B 20 9F F2 4E 35 5E D3 92 21 53 ED 9A F1 8F 14 D0 02 73 E0 62 AD C3 A3 79 21 A2 6A 66 19 D2 A5 C7 E3')  #
        info.share_key = bytes.fromhex('0E6F09415FC0A5CCD040AFA92EBE3EB0')
        info.key_rand = bytes.fromhex('944C10A69E2A5E4CEEF08512BA3B39FE')
        info.key_tg = bytes.fromhex('AD 07 ED 80 67 75 BB F7 FD C4 A8 D5 41 5E 73 EA')
        info.Guid = bytes.fromhex('9b6be0653a356f4fac89926f3f1ceb7e')
        # 手机协议-
        methods = [
            _tlv.T018,
            _tlv.T001,
            _tlv.T106,
            _tlv.T116,
            _tlv.T100,
            _tlv.T107,
            _tlv.T142,
            _tlv.T144,
            _tlv.T145,
            _tlv.T147,
            _tlv.T154,
            _tlv.T141,
            _tlv.T008,
            _tlv.T511,
            _tlv.T187,
            _tlv.T188,
            _tlv.T191,
            _tlv.T177,
            _tlv.T516,
            _tlv.T521,
            _tlv.T525
        ]

        # pass

    pack.add_Hex('00 09')
    pack.add_int(len(methods), 2)  # 数量

    for method_result in methods:
        pack.add_bin(method_result)
    _data = pack.get_bytes()

    data = TEA.encrypt(_data, info.share_key)

    # 头部
    pack = pack_b()
    pack.add_Hex('1F 41')
    pack.add_Hex('08 10')
    pack.add_Hex('00 01')
    pack.add_int(int(info.uin))  # Uin_bytes
    if info.device.client_type == 'Watch':
        pack.add_Hex('03 07 00 00 00 00 02 00 00 00 00 00 00 00 00')
        pack.add_Hex('01 01')
        pack.add_bin(info.key_rand)  # 不是key
        pack.add_Hex('01 02')

    else:
        # 默认普通QQ
        pack.add_Hex('03 87 00 00 00 00 02 00 00 00 00 00 00 00 00')
        pack.add_Hex('02 01')
        pack.add_bin(info.key_rand)  # 不是key
        pack.add_Hex('01 31')
        pack.add_Hex('00 01')

    pack.add_body(info.key_Pubkey, 2)

    pack.add_bin(data)
    data = pack.get_bytes()

    pack.empty()  # 包裹
    pack.add_Hex('02')
    pack.add_body(data, 2, add_len=4)

    pack.add_Hex('03')
    data = pack.get_bytes()
    # 头部
    data = Pack_Head_login(info, 'wtlogin.login', data)

    data = Pack_(info, data=data, encryption=2, Types=10, sso_seq=4)

    return data


def login_res(data, info):
    data = data[15:-1]  # 头部 15字节&去掉尾部03
    _status = data[0]
    data = TEA.decrypt(data[1:], info.share_key)
    if _status == 0:
        data = data[5:]  # 00 09 00 00 02

        pack = pack_u(data)
        _head = pack.get_bin(2).hex()
        _len = pack.get_short()
        data = pack.get_bin(_len)

        if _head == '0119':
            # 判断tlv的头部
            data = TEA.decrypt(data, info.key_tgtgt)
    else:
        data = data[3:]
    un_tlv = Un_Tlv(data, info)

    print('登录返回', _status, un_tlv.unpack())


def login_captcha(info, Ticket: str):
    """登录验证码"""
    _tlv = TLV(info)
    pack = pack_b()
    methods = [
        _tlv.T193(Ticket),
        _tlv.T008(),
        _tlv.T104(),
        _tlv.T116(),
        _tlv.T547(),
    ]
    pack.add_Hex('00 02')
    pack.add_int(len(methods), 2)  # 数量

    for method_result in methods:
        pack.add_bin(method_result)
    _data = pack.get_bytes()
    # _data = bytes.fromhex(
    #     '00 02 00 05 01 93 00 8F 74 30 33 53 58 38 37 52 4B 55 51 31 66 61 7A 4A 7A 58 33 56 53 54 5A 54 6E 30 6D 4B 7A 70 6A 4C 71 52 4F 64 61 42 36 31 53 41 45 6E 52 30 43 65 34 52 50 59 6A 34 69 7A 41 68 52 46 78 78 66 6D 67 6D 41 39 59 54 6A 71 58 6D 62 30 6F 52 64 59 47 46 49 6B 43 78 66 32 65 73 33 52 65 6F 4C 34 72 51 75 57 59 71 42 41 4A 70 76 52 68 6D 71 54 41 6B 45 5F 53 53 51 73 73 46 4D 64 44 37 41 31 77 64 43 4B 49 77 71 69 65 46 68 59 37 77 2A 00 08 00 08 00 00 00 00 08 04 00 00 01 04 00 24 41 6C 5A 47 50 32 35 46 73 4B 45 4D 34 59 32 4D 7A 76 6F 34 79 58 7A 70 57 74 6A 43 57 47 32 31 6F 67 3D 3D 01 16 00 0E 00 0A F7 FF 7C 00 01 04 00 01 5F 5E 10 E2 05 47 00 14 01 02 01 01 01 00 00 00 00 02 27 10 00 00 00 21 00 00 27 10')
    data = TEA.encrypt(_data, info.share_key)

    # 头部
    pack = pack_b()
    pack.add_Hex('1F 41')
    pack.add_Hex('08 10')
    pack.add_Hex('00 01')
    pack.add_int(int(info.uin))  # Uin_bytes

    pack.add_Hex('03 07 00 00 00 00 02 00 00 00 00 00 00 00 00')
    pack.add_Hex('02 01')
    pack.add_bin(info.key_rand)  # 不是key
    pack.add_Hex('01 31')
    pack.add_Hex('00 01')

    pack.add_body(info.key_Pubkey, 2)

    pack.add_bin(data)
    data = pack.get_bytes()

    pack.empty()  # 包裹
    pack.add_Hex('02')
    pack.add_body(data, 2, add_len=4)

    pack.add_Hex('03')
    data = pack.get_bytes()
    # 头部
    data = Pack_Head_login(info, 'wtlogin.login', data)

    data = Pack_(info, data=data, encryption=2, Types=10, sso_seq=4)
    return data


def wtlogin_trans(bArr):
    """k值 变体解法"""
    a_sm = b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff' \
           b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff>\xff\xff?\xff\xff456789:;<=\xff\xff\xff' \
           b'\xff\xff\xff\xff\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16' \
           b'\x17\x18\x19\xff\xff\xff\xff\xff\xff\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,' \
           b'-./0123\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff' \
           b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff' \
           b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff' \
           b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff' \
           b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff' \
           b'\xff\xff\xff\xff\xff'
    if isinstance(bArr, str):
        bArr = bArr.encode()

    i = 32
    i4 = 0
    i3 = 0
    i2 = 0
    b = 0
    bArr2 = bytearray(24)
    while True:
        i6 = i - 1
        if i > 0:
            i7 = i4 + 1
            i5 = bArr[i4]

            if i5 != 0 or i5 == 95:
                if i5 == 32:
                    i5 = 42

                b2 = a_sm[i5]
                if b2 < 0:
                    b = b2
                    i = i6
                    i4 = i7
                else:
                    residue = i3 % 4
                    if residue == 0:
                        bArr2[i2] = b2 << 2
                        i5 = i2
                    elif residue == 1:
                        i5 = i2 + 1

                        bArr2[i2] = bArr2[i2] | (b2 >> 4)
                        bArr2[i5] = (b2 & 0x0F) << 4

                    elif residue == 2:
                        i5 = i2 + 1
                        bArr2[i2] = bArr2[i2] | (b2 >> 2)
                        bArr2[i5] = (b2 & 0x03) << 6
                    elif residue == 3:
                        i5 = i2 + 1
                        bArr2[i2] |= b2
                    else:
                        i5 = i2

                i3 += 1
                i4 = i7
                i = i6
                i2 = i5
                b = b2


        elif b == 95:
            residue = i3 / 4
            if residue == 1:
                break
            elif residue == 2:
                i2 = i2 + 1
        else:
            break

    return bArr2


def trans_emp(info, verify=None):
    if verify:
        # 扫码状态
        pack = pack_b()
        pack.add_Hex('00 00 62 00 00 00 10 00 00 00 72 00 00 00')
        pack.add_int(int(time.time()))
        pack.add_Hex('02 00 5E 00 12 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 03 00 00 00 32 00 '
                     '00 00 01 00 00 00 00 00 00 00 00 00 05 01 00 00 00 73 00 00')
        pack.add_Hex('00 10 ')
        pack.add_int(len(info.UN_Tlv_list.T100_qr_code_mark), 2)
        pack.add_bin(info.UN_Tlv_list.T100_qr_code_mark)
        pack.add_Hex('00 00 00 00 00 00 00 00 08 00 00 00 00 03')

        data = pack.get_bytes()
    else:
        # 获取二维码
        pack = pack_b()
        pack.add_Hex(
            '00 01 0D 00 00 00 10 00 00 00 72 00 00 00 64 C9 FA 20 02 01 09 00 31 00 00 00 00 00 00 00 00 00 00 00 00 '
            '00'
            '00 00 00 00 00 00 00 00 03 00 00 00 32 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 10 00 00 00 00 '
            '00'
            '00 00 00 08 00 00 00 06')
        Tlv = TLV(info)
        pack.add_bin(Tlv.T016())
        pack.add_bin(Tlv.T01B())
        pack.add_bin(Tlv.T01D())
        pack.add_bin(Tlv.T01F())
        pack.add_bin(Tlv.T033())
        pack.add_bin(Tlv.T035())
        pack.add_Hex('03')
        data = pack.get_bytes()
    data = TEA.encrypt(data, info.share_key)
    # 头部
    pack = pack_b()
    pack.add_Hex('1F 41')
    pack.add_Hex('08 12')
    pack.add_Hex('00 01')
    pack.add_Hex('00 00 00 00')  # Uin_bytes
    pack.add_Hex('03 07 00 00 00 00 02 00 00 00 00 00 00 00 00')

    pack.add_Hex('01 01')  # 变化01

    pack.add_bin(info.key_rand)
    pack.add_Hex('01 02')
    pack.add_int(len(info.key_Pubkey), 2)
    pack.add_bin(info.key_Pubkey)
    pack.add_bin(data)
    data = pack.get_bytes()

    pack.empty()  # 包裹
    pack.add_Hex('02')
    pack.add_int(len(data) + 4, 2)  # 短整数
    pack.add_bin(data)
    pack.add_Hex('03')
    data = pack.get_bytes()

    # 头部
    data = Pack_Head_login(info, 'wtlogin.trans_emp', data)
    data = Pack_(info, data=data, encryption=2, Types=10, sso_seq=4)
    return data


def trans_emp_auth(info, **kwargs):
    verify = kwargs.get('verify', False)
    pack = pack_b()
    pack.add_int(int(time.time()))

    if verify:
        pack.add_Hex(
            '02 00 C9 00 14 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 03 00 00 00 32 00 00 00 02 00 00 00 00')
    else:
        pack.add_Hex(
            '02 00 DE 00 13 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 03 00 00 00 32 00 00 00 00 00 00 00 00')

    pack.add_int(int(info.uin))
    pack.add_Hex('00 00 00 00 00 10 00 00 00 00')
    pack.add_int(int(info.uin))
    pack.add_body(wtlogin_trans(kwargs['K']), 2)
    pack.add_body(info.UN_Tlv_list.T10A_token_A4, 2)
    if verify:
        pack.add_Hex('08 00 03 00 02 00 08 00 00 00 00 00 00 00 0B 00 15 00 04 00 00 00 00 00 68')
        pack.add_body(info.Guid, 2)
    else:
        pack.add_bin(info.Guid)
        pack.add_Hex('01 00 01 08 00 04 00 03 00 05 00 20 00 36 00 01 00 09')
        pack.add_body('com.tencent.mobileqq', 2)  # 似乎会对其识别
        pack.add_Hex('00 39 00 04 00 00 00 01')

    pack.add_Hex('03')
    data = TEA.encrypt(pack.get_bytes(), info.UN_Tlv_list.T10E)

    pack.empty()
    if verify:
        pack.add_Hex('01 00 D8 00 00 00 10 00 00 00 72 00 60')
    else:
        pack.add_Hex('01 00 F0 00 00 00 10 00 00 00 72 00 60')
    pack.add_bin(info.UN_Tlv_list.T114)
    pack.add_Hex('00')
    pack.add_bin(data)

    data = TEA.encrypt(pack.get_bytes(), info.UN_Tlv_list.T134)

    pack.empty()
    pack.add_Hex('1F 41')
    pack.add_Hex('08 12')
    pack.add_Hex('00 01')
    pack.add_int(int(info.uin))  # Uin_bytes
    pack.add_Hex('03 45 00 00 00 00 02 00 00 00 00 00 00 00 00 00 30')
    pack.add_bin(info.UN_Tlv_list.T133)
    pack.add_bin(data)

    data = pack.get_bytes()

    pack.empty()  # 包裹
    pack.add_Hex('02')
    pack.add_int(len(data) + 4, 2)  # 短整数
    pack.add_bin(data)
    pack.add_Hex('03')

    data = pack.get_bytes()

    pack.empty()
    pack.add_Hex(
        '00 00 00 27 00 00 00 15 77 74 6C 6F 67 69 6E 2E 74 72 61 6E 73 5F 65 6D 70 00 00 00 08 F7 C0 A1 E8 00 00 00 06 70 00')
    pack.add_int(len(data) + 4, 4)
    pack.add_bin(data)
    data = TEA.encrypt(pack.get_bytes(), '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00')
    # 头部
    data = Pack_(info, data=data, encryption=2, Types=11, sso_seq=info.seq)
    return data


def trans_emp_auth_res(data, info, **kwargs):
    auth_info = {}
    verify = kwargs.get('verify', False)
    auth_info['verify'] = verify
    data = TEA.decrypt(data[16:-1], info.UN_Tlv_list.T134)
    data = TEA.decrypt(data[5:], info.UN_Tlv_list.T10E)
    data = data[53:]
    pack = pack_u(data)
    status = pack.get_byte()

    if status != 0:
        _len = pack.get_short()
        message = pack.get_bin(_len).decode('utf-8')
        auth_info['message'] = message
    else:
        _time = pack.get_int(4)
        _len = pack.get_short()
        AuthName = pack.get_bin(_len).decode('utf-8')
        auth_info['AuthName'] = AuthName
        if verify:
            # 确认授权
            pack.get_short()
        data = pack.get_all()
        TLv = Un_Tlv(data, info)
        TLv.unpack()

        auth_info.update(TLv.get_auth_result())
    auth_info['status'] = status
    return auth_info


def trans_emp_res(data, info, verify):
    status_message = {
        48: '请使用手机QQ扫描二维码登录',
        53: '扫描成功,请在手机上确认登录',
        54: '用户已取消登录',
        99: '请扫描二维码',
        0: '完成授权'
    }
    pack = pack_u(data)
    pack.get_byte()  # 02
    pack.get_int(2)  # len

    pack = pack_u(pack.get_all())
    pack.get_bin(10)  # 1f 41 08 12 00 01 00 00 00 00
    pack.get_int(2)  # ?
    pack.get_byte()  # ?
    data = pack.get_all()

    data = TEA.decrypt(data[:-1], info.share_key)
    if verify:
        status = data[-2]
        qrCode = None
        if status == 0:
            data = data[72:]
            Un_Tlv(data, info).unpack()

            print('扫码完成', data.hex())


    else:
        status = 99

        data = data[53:]  # 去掉前面
        pack = pack_u(data)
        pack.get_bin(2)  # tlv
        _len = pack.get_int(2)  # len
        info.UN_Tlv_list.T100_qr_code_mark = pack.get_bin(_len)  # data
        pack.get_bin(2)  # tlv
        pack.get_int(2)  # len
        _len = pack.get_int(2)
        qrCode = pack.get_bin(_len)  # data
    message = status_message.get(status, "未知状态")
    return qrCode, status, message
