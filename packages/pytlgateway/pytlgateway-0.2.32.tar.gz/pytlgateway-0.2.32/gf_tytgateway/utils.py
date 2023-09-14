from datetime import datetime, timedelta
import chardet
import argparse


def encode_gf_side(side):
    rtn_trade_side = 0
    if side == "0B":
        rtn_trade_side = 1
    elif side == "0S":
        rtn_trade_side = 2
    elif side == "4B":
        rtn_trade_side = 3
    return rtn_trade_side


def decode_gf_status(status):
    new_status = ""
    if status in ['2', '7']:
        new_status = 'active'
    elif status == '8':
        new_status = 'filled'
    elif status in ['5', '6']:
        new_status = 'canceled'
    return new_status

def side_to_target_type(side):
    target_type = ""
    if side == 1:
        target_type = "buy"
    elif side == 2:
        target_type = "sell"
    return target_type

def decode_exchange_id(exchange):
    if exchange.startswith('6'):
        exchange = 101
    elif exchange.startswith('0'):
        exchange = 102
    else:
        exchange = 102

    return exchange

def encode_gf_market(stock_code):
    exchange = ""
    if stock_code.startswith('6'):
        exchange = '1'
    elif stock_code.startswith('0'):
        exchange = '0'
    else:
        exchange = '0'

    return exchange

"""
上海'1'，深圳'0'，沪港通 '8'，深圳通'G'，中金'F'，上期'H'，郑商'Z'，大商'D
"""
def decode_gf_market(market):
    exchange = 0
    if market == '0':
        exchange = 102
    elif market == '1':
        exchange = 101
    return exchange

def get_today_date():
    return datetime.today().strftime('%Y%m%d')

def decode_ordtype(order_type:str):
    ord_type = -1
    mapping = {
        'vwap': '1001',
        'twap': '1002',
        'kf_vwap_plus': '3001',
        'kf_twap_plus': '3002'
    }
    ord_type = mapping.get(order_type, -1)
    return ord_type

def check_charset(file_path):
    with open(file_path, "rb") as f:
        data = f.read(4)
        charset = chardet.detect(data)['encoding']
    return charset

def get_time_from_str(time_str):
    
    today = datetime.now().date()
    datetime_str = f"{today} {time_str}"
    dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    utc_dt = dt - timedelta(hours=8)
    
    return utc_dt

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')