import random
import uuid
import time

uuid_node = random.randint(100000000, 999999999)  # 避免泄密设备信息


def random_mac_uuid():
    """
    uuid1
    由MAC地址、当前时间戳、随机数生成。可以保证全球范围内的唯一性，
    但MAC的使用同时带来安全性问题，局域网中可以使用IP来代替MAC。
    这里使用随机数代替
    """
    return str(uuid.uuid1(node=uuid_node))  # 替换原来的MAC地址为随机数


def timestamp_uuid():
    """
    使用纳秒级别时间戳+uuid作为id
    """
    return f'{time.time_ns()}_{random_mac_uuid()}'
