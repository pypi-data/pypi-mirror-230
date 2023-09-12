import kuto

from page.ios_page import *


class TestIosDemo(kuto.Case):
    """IOS应用demo"""

    def start(self):
        self.index_page = IndexPage(self.driver)
        self.my_page = MyPage(self.driver)
        self.set_page = SettingPage(self.driver)

    def test_go_setting(self):
        self.index_page.myTab.click()
        self.my_page.settingBtn.click()
        self.set_page.about.assert_exists()


if __name__ == '__main__':
    """仅执行本模块"""
    kuto.main(
        platform="ios",
        device_id="00008101-000E646A3C29003A",
        pkg_name='com.qizhidao.company'
    )


