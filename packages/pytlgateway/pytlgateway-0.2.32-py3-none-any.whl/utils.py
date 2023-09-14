import sys
import os

def decode_exchange_id(suffix):
    exchange = 0
    if suffix == 'SH':
        exchange = 101        #EXCHANGE_SSE 
    elif suffix == 'SZ':
        exchange = 102        #EXCHANGE_SZE 
    
    return exchange

def get_log_default_path():
    # python2: linux2, python3: linux
    if sys.platform.startswith("linux") or sys.platform == "darwin":
        dirs = "/shared/log"
    elif sys.platform == "win32":
        dirs = os.path.join(get_windows_first_disk() + "/tmp/linker/log")
    else:
        dirs = '.'

    return dirs


def get_digit_from_env(env_name, default_num):
    num = str(os.environ.get(env_name))
    return int(num) if num.isdigit() else default_num

def get_log_given_path(path):
    dirs = os.path.join(path)
    return path