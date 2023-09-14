import inspect
import json
import os
import pytest
import psutil

from kuto.utils.config import config, free_config
from kuto.utils.log import logger
from kuto.core.android.common import get_connected_adr_devices
from kuto.core.ios.common import get_connected_ios_devices


class TestMain(object):
    """
    Support for app、web、http
    """
    def __init__(self,
                 platform: str = None,
                 device_id=None,
                 pkg_name: str = None,
                 start: bool = True,
                 brow: str = None,
                 headless: bool = False,
                 path: str = None,
                 rerun: int = 0,
                 xdist: bool = False,
                 host: str = None,
                 headers: dict = None,
                 state: dict = None,
                 cookies: list = None
                 ):
        """
        @param platform: 测试平台，android、ios、web、api
        @param device_id: 设备id，针对安卓和ios，可以是str和list，
        对安卓和ios来说也可以是远程服务
        @param pkg_name: 应用包名，针对安卓和ios
        @param start: 是否默认启动应用，针对安卓和ios
        @param brow: 浏览器类型，chrome、firefox、webkit
        @param path: 用例目录，None默认代表当前文件
        @param rerun: 失败重试次数
        @param xdist: 是否使用多进程执行
        @param host: 域名，针对接口和web
        @param headers: {
            "login": {},
            "visit": {}
        }
        @param state: 通过playwright的storage_state方法获取
        @param cookies:
        """

        # 公共参数保存
        config.set_common("platform", platform)
        # api参数保存
        config.set_api("base_url", host)
        if headers:
            if 'login' not in headers.keys():
                raise KeyError("without login key!!!")
            login_ = headers.pop('login', {})
            config.set_api('login', login_)
            visit_ = headers.pop('visit', {})
            config.set_api('visit', visit_)
        # app参数保存
        # 增加一段逻辑支持多进程以及设备调度
        # 把所有的设备id加入到空闲设备列表中（用文件保存）
        free_devices = []
        if device_id is None:
            # 获取当前连接的手机列表
            if platform == "android":
                free_devices = get_connected_adr_devices()
            elif platform == "ios":
                free_devices = get_connected_ios_devices()
            free_config.add_devices(free_devices)
        else:
            if isinstance(device_id, str):
                free_devices = [device_id]
                free_config.add_devices(free_devices)
            if isinstance(device_id, list):
                if xdist is True:
                    # 如果需要并发，才把所有设备放入空闲列表
                    free_devices = device_id
                    free_config.add_devices(free_devices)
                else:
                    # 如果不需要并发，把第一个设备放入空闲列表
                    free_devices = device_id[0:1]
                    free_config.add_devices(free_devices)
        config.set_app("pkg_name", pkg_name)
        config.set_app("auto_start", start)
        # web参数保存
        config.set_web("base_url", host)
        config.set_web("browser_name", brow)
        config.set_web("headless", headless)
        if state:
            config.set_web("state", json.dumps(state))
        if cookies:
            config.set_web("cookies", json.dumps(cookies))

        # 执行用例
        # logger.info('执行用例')
        if path is None:
            stack_t = inspect.stack()
            ins = inspect.getframeinfo(stack_t[1][0])
            file_dir = os.path.dirname(os.path.abspath(ins.filename))
            file_path = ins.filename
            if "\\" in file_path:
                this_file = file_path.split("\\")[-1]
            elif "/" in file_path:
                this_file = file_path.split("/")[-1]
            else:
                this_file = file_path
            path = os.path.join(file_dir, this_file)
        cmd_list = [
            '-sv',
            '--reruns', str(rerun),
            '--alluredir', 'report', '--clean-alluredir'
        ]
        if path:
            cmd_list.insert(0, path)
        if xdist:
            if platform in ["android", "ios"]:
                if len(free_devices) > 1:
                    # 设备数大于1才开启多进程
                    n = len(free_devices)
                    cpu_count = psutil.cpu_count()
                    if n > cpu_count:
                        n = cpu_count
                    cmd_list.insert(1, '-n')
                    cmd_list.insert(2, str(n))
            else:
                cmd_list.insert(1, '-n')
                cmd_list.insert(2, 'auto')
        logger.info(cmd_list)
        pytest.main(cmd_list)

        # 公共参数保存
        # api参数保存
        config.set_api("base_url", None)
        config.set_api('login', {})
        config.set_api('visit', {})
        # app参数保存
        # 增加一段逻辑支持多进程以及设备调度
        # 清空空闲设备列表
        free_config.clear_devices()
        config.set_app("device_id", None)
        config.set_app("pkg_name", None)
        config.set_app("auto_start", False)
        # config.set_app("errors", [])
        # web参数保存
        config.set_web("base_url", None)
        config.set_web("browser_name", "chrome")
        config.set_web("headless", False)
        config.set_web("state", None)
        config.set_web("cookies", None)


main = TestMain


if __name__ == '__main__':
    main()

