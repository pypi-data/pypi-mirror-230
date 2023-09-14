"""
@Author: kang.yang
@Date: 2023/7/31 18:14
"""
from kuto import AndroidDriver, AdrElem

driver = AndroidDriver(device_id='UJK0220521066836',
                       pkg_name='com.qizhidao.clientapp')
driver.start_app()
AdrElem(driver, rid='com.qizhidao.clientapp:id/btn_login').click()
AdrElem(driver, text='其他手机号码登录').click()
AdrElem(driver, text='帐号密码登录').click()
AdrElem(driver, rid='com.qizhidao.clientapp:id/phone_et').input_exists("13652435335")
AdrElem(driver, rid='com.qizhidao.clientapp:id/clear_edit_text').input_pwd("wz123456@QZD")
AdrElem(driver, rid='com.qizhidao.clientapp:id/pwd_check_box_layout').click_exists()
AdrElem(driver, text='登录').click()
AdrElem(driver, rid='com.qizhidao.clientapp:id/common_list_rv').click_exists()
AdrElem(driver, rid='com.qizhidao.clientapp:id/skip_btn').click_exists()
driver.assert_act('.main.HomeActivity')
driver.stop_app()



