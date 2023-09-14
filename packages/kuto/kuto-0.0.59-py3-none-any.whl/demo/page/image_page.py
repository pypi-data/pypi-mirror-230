"""
@Author: kang.yang
@Date: 2023/8/21 17:10
"""
import kuto

"""
图像识别可以配合安卓应用或者IOS应用使用
"""


class ImagePage(kuto.Page):
    searchEntry = kuto.AdrElem(
        desc='搜索框入口',
        rid="com.tencent.mm:id/j5t"
    )
    searchInput = kuto.AdrElem(
        desc='搜索框',
        rid="com.tencent.mm:id/cd7"
    )
    searchResult = kuto.AdrElem(
        desc="搜索结果",
        rid="com.tencent.mm:id/kpm"
    )
    schoolEntry = kuto.ImageElem(
        desc='校园场馆入口',
        image="../static/校园场馆.png"
    )

