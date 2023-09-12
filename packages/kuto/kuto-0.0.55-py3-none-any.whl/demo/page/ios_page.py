"""
@Author: kang.yang
@Date: 202
3/8/1 16:27
"""
from kuto import Page, IosElem as Elem


"""
定位方式：优先选择label
name: 根据name属性进行定位
label: 根据label属性进行定位
value: 根据value属性进行定位
text: 根据文本属性进行定位，集合和label、value等文本属性的内容
cname: 根据className属性进行定位
xpath: 根据xpath进行定位
index: 获取到定位到的第index个元素
"""


class IndexPage(Page):
    """首页"""
    adBtn = Elem(text='close white big')
    myTab = Elem(text='我的')


class MyPage(Page):
    """我的页"""
    settingBtn = Elem(text='settings navi')


class SettingPage(Page):
    """设置页"""
    about = Elem(text="关于企知道")
