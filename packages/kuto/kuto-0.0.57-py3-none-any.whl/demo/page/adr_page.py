"""
@Author: kang.yang
@Date: 2023/8/1 11:53
"""
from kuto import Page, AdrElem as Elem

"""
定位方式：优先选择rid
rid: 根据resourceId进行定位
text：根据text属性进行定位
cname：根据className属性进行定位
xpath：根据xpath进行定位
index：获取定位到的第index个元素
"""


class HomePage(Page):
    """APP首页"""
    adBtn = Elem(rid='com.qizhidao.clientapp:id/bottom_btn')
    myTab = Elem(xpath='//*[@resource-id="com.qizhidao.clientapp:id/ll'
                    'BottomTabs"]/android.widget.FrameLayout[4]')
    spaceTab = Elem(text='科创空间')


class MyPage(Page):
    """我的页"""
    settingBtn = Elem(rid='com.qizhidao.clientapp:id/me_top_bar_setting_iv')


class SettingPage(Page):
    """设置页"""
    title = Elem(rid='com.qizhidao.clientapp:id/tv_actionbar_title')
    agreementText = Elem(rid='com.qizhidao.clientapp:id/agreement_tv_2')
