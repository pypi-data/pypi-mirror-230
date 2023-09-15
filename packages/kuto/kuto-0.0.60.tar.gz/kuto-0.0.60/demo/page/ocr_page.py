"""
@Author: kang.yang
@Date: 2023/8/21 17:05
"""
import kuto

"""
ocr识别可以配合安卓应用或者IOS应用进行使用
"""


class OcrPage(kuto.Page):
    searchBtn = kuto.IosElem(text="搜索", className="XCUIElementTypeSearchField", desc='搜索框入口')
    searchInput = kuto.IosElem(className="XCUIElementTypeSearchField", desc='搜索框')
    searchResult = kuto.IosElem(xpath="//Table/Cell[2]", desc='搜索结果')
    schoolEntry = kuto.OCRElem(text="校园场馆", pos=12)

