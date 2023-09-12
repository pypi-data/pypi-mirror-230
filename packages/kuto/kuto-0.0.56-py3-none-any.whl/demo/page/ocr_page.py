"""
@Author: kang.yang
@Date: 2023/8/21 17:05
"""
import kuto

"""
ocr识别可以配合安卓应用或者IOS应用进行使用
"""


class OcrPage(kuto.Page):
    searchBtn = kuto.IosElem(text="搜索", cname="XCUIElementTypeSearchField")
    searchInput = kuto.IosElem(cname="XCUIElementTypeSearchField")
    searchResult = kuto.IosElem(xpath="//Table/Cell[2]")
    schoolEntry = kuto.OCRElem(text="校园场馆", pos=12)
