import os, sys, pathlib
import time
from pathlib import Path


def start_emqx_server():
    print(f'system is {sys.platform}')
    if sys.platform == 'win32':
        pass
    else:
        raise NotImplementedError('only support windows now')

    # check emqx server
    if check_emqx_server():
        return
    print(f'starting emqx server')
    # if path not exists, create it
    emqx_path = Path(r'emqx\bin\emqx')
    # start emqx by run "emqx\bin\emqx start"
    os.system(f"{emqx_path} start")
    print('emqx server started')


def check_emqx_server():
    print(f'check emqx server')
    # if path not exists, create it
    emqx_path = Path(r'emqx\bin\emqx_ctl')
    # 检测emqx是否正在运行
    # run "emqx\bin\emqx status" and get the result
    result = os.popen(f"{emqx_path} status").read()
    print(f'emqx status is {result}')
    if 'is starting' in result:
        print('emqx server is starting check again after 3 seconds')
        time.sleep(3)
        return check_emqx_server()
    if 'is started' in result:
        print('emqx server is running')
        return True
    else:
        print('emqx server is not running')
        return False


def test_emqx_server():
    start_emqx_server()

if __name__ == '__main__':
    test_emqx_server()
