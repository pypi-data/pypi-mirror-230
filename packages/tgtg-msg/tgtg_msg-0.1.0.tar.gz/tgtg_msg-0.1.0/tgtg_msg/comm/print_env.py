import os
from .parse_tuple import parse_tuple


def print_env():
    print(f'NO_DEF:{os.getenv("NO_DEF")}')
    print(f'TEMP:{os.getenv("TEMP")}')
    print(f'GOPATH:{os.getenv("GOPATH")}')

    print(f'MY_PROXY:{os.getenv("MY_PROXY")}')
    print(f'MY_PROXY type:{type(os.getenv("MY_PROXY"))}')
    print(f'MY_PROXY tuple:{parse_tuple(os.getenv("MY_PROXY"))}')

