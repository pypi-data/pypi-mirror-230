"""
@Author: kang.yang
@Date: 2023/8/21 17:05
"""
import kuto

"""
ocr识别可以配合安卓应用或者IOS应用进行使用
"""


class OcrPage(kuto.Page):
    searchBtn = kuto.IosElem(
        desc='搜索框入口',
        text="搜索",
        className="XCUIElementTypeSearchField"
    )
    searchInput = kuto.IosElem(
        desc='搜索框',
        className="XCUIElementTypeSearchField"
    )
    searchResult = kuto.IosElem(
        desc='搜索结果',
        xpath="//Table/Cell[2]"
    )
    schoolEntry = kuto.OCRElem(
        text="校园场馆",
        pos=12
    )
