# -*- coding: utf-8 -*-
# @Time    : 2023/3/8 17:54:32
# @Author  : Pane Li
# @File    : base_page.py
"""
base_page

"""
import os.path
import time
from os import path
import playwright
from inhandtest.base_page._ig_contents_locators import IGContentsLocators
from typing import List
from inhandtest.exception import ModelError
from inhandtest.tools import replace_str
from playwright.sync_api import Page, Locator, expect, TimeoutError, sync_playwright
from inhandtest.base_page._vg710_contents_locators import VGContentsLocators
from inhandtest.base_page._ir3XX_contents_locators import Ir3XXContentsLocators
from inhandtest.base_page.table_tr import Table, IgTable
from collections import Counter
import allure
import re
import logging
import base64


class BasePage:

    def __init__(self, host: str, username: str, password: str, protocol='https',
                 port=443, model='VG710', language='en', page: Page = None, **kwargs):
        """

        :param host:  设备主机地址
        :param username: 用户名
        :param password: 密码
        :param protocol: 协议
        :param port: 端口
        :param model: 'VG710'|'ER805'|'ER605'|'IR302'|'IG502'|'IG902'|'IR305'|'IR615'
        :param page: 当page为None时，自动打开浏览器及页面，否则使用传入的page
        :param kwargs:
                      browser: 当没有传入page时，可以选择浏览器
                      locale: dict 国际化
                      bring_to_front: bool 是否将浏览器窗口置顶
                      viewport: {'width': 1366, 'height': 768}  浏览器窗口大小
                      web_login_timeout: int  登录超时时间 默认300， 单位秒 即5分钟， 监测到登录超时后，会自动重新登录
        """
        self.page = page
        self.host = host
        self.model = model.upper()
        self.protocol = protocol
        self.port = port
        self.username = username
        self.password = password
        self.language = language
        self.bring_to_front = kwargs.get('bring_to_front', False)
        self.__browser_type = kwargs.get('browser')
        self.__http_credentials_model = ('VG710',)  # 需要使用http认证的设备, 没有登录页面 只有登录弹窗
        self.__web_login_timeout = kwargs.get('web_login_timeout', 300)
        self.__logout_time = None
        self.viewport = kwargs.get('viewport', {'width': 1366, 'height': 768})
        if self.page is None:
            self.__new_page()
        if self.model == 'VG710':
            self.content_locator = VGContentsLocators(self.page, language).tags_menu
        elif self.model in ('IG902', 'IG502'):
            self.content_locator = IGContentsLocators(self.page, language).tags_menu
        elif self.model in ('IR302', 'IR305', 'IR615'):
            self.content_locator = Ir3XXContentsLocators(self.page, language).tags_menu
        else:
            logging.exception(f'not support this mode {model}')
            raise ModelError(f'not support this mode {model}')
        self.locale = kwargs.get('locale').get(language) if kwargs.get('locale') else None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def call_web_login_timeout(self, response):
        if response.status == 401:
            # 当页面的token过期时，可能会连续几个API返回401，这里只处理一次，避免重复登录
            if self.__logout_time is None or (int(time.time()) - self.__logout_time) > self.__web_login_timeout:
                logging.warning(f'login timeout, try to login again')
                self.__logout_time = int(time.time())
                self.login(self.username, self.password)

    @property
    def __login_locator(self) -> dict:
        if self.model == 'VG710':
            return {'wait_locator': self.page.locator('#logo')}
        elif self.model in ('ER805', 'ER605'):
            return {'username': self.page.locator('#username'), 'password': self.page.locator('#password'),
                    'submit': self.page.locator('button'),
                    'wait_locator': self.page.locator('.inStarCloud')}
        elif self.model in ('IG902', 'IG502'):
            return {'username': self.page.locator('#username'), 'password': self.page.locator('#password'),
                    'submit': self.page.locator('//button[@type="submit"]'),
                    'wait_locator': self.page.locator('#logo')}
        elif self.model == 'IR302':
            return {'username': self.page.locator('#username'), 'password': self.page.locator('#passwd'),
                    'submit': self.page.locator('.login_button'),
                    'wait_locator': self.page.locator('#logo')}
        else:
            logging.exception(f'not support this model {self.model}')
            raise Exception(f'not support this model {self.model}')

    def __new_page(self):
        def dialog_(dialog):
            logging.debug(f'dialog message is {dialog.message}, accepted')
            dialog.accept()

        self.__playwright = sync_playwright().start()
        if self.__browser_type == 'firefox':
            browser = self.__playwright.firefox
        elif self.__browser_type == 'webkit':
            browser = self.__playwright.webkit
        else:
            browser = self.__playwright.chromium
        self.__browser = browser.launch(headless=False)
        if self.model in self.__http_credentials_model:
            http_credentials = {'username': self.username, 'password': self.password}
        else:
            http_credentials = None
        self.__context = self.__browser.new_context(ignore_https_errors=True, http_credentials=http_credentials,
                                                    viewport=self.viewport, permissions=['clipboard-read'])
        logging.info('Start your journey browser is chrome')
        self.page = self.__context.new_page()
        self.page.on("dialog", dialog_)

    @allure.step("用户登录")
    def login(self, username=None, password=None, status='success') -> None:
        """

        :param username:  如果不传使用默认的用户名
        :param password:  如果不传使用默认的密码
        :param status: 登录状态 'success'|'fail' 期望登录的状态是成功还是失败，失败了就会停留在登录页面，不做任何操作
        :return:
        """
        username = self.username if not username else username
        password = self.password if not password else password

        def goto_router():
            device = "{}://{}:{}".format(self.protocol, self.host, self.port)
            try:
                self.page.goto(device, timeout=120 * 1000)
            except Exception:
                logging.exception(f'Open {self.host} device address {device} timeout')
                raise
            if self.bring_to_front:
                self.page.bring_to_front()
            self.page.wait_for_timeout(500)
            if self.model in self.__http_credentials_model:
                logging.info(f'Open {self.host} device address {device} and login')
            else:
                logging.info(f'Open {self.host} device address {device}')

        def _login():
            if self.model not in self.__http_credentials_model:
                self.__login_locator.get('username').fill(username)
                logging.debug('Device %s fill username %s' % (self.host, username))
                self.__login_locator.get('password').fill(password)
                logging.debug('Device %s fill password %s' % (self.host, password))
                self.__login_locator.get('submit').click()
                logging.info("Device %s  login" % self.host)
                if status == 'success':
                    self.__login_locator.get('wait_locator').wait_for(state='visible')
                    self.page.wait_for_timeout(500)

        self.page.wait_for_load_state('domcontentloaded', timeout=15 * 1000)
        if self.__login_locator.get('username') and self.__login_locator.get('username').is_visible():
            _login()
        elif self.__login_locator.get('wait_locator') and self.__login_locator.get(
                'wait_locator').is_visible():
            pass
        elif self.page.url == 'about:blank':
            goto_router()
            _login()
        else:
            try:
                self.page.reload()
                logging.debug(f"Device %s refresh page" % self.host)
                self.__login_locator.get('wait_locator').wait_for(state='visible', timeout=10 * 1000)
            except TimeoutError:
                if self.__login_locator.get('username') and self.__login_locator.get(
                        'username').is_visible():
                    _login()
                else:
                    logging.error(f"Device {self.host} page is error")

    @allure.step('页面抓取接口返回结果')
    def wait_for_response(self, url: str, timeout=30) -> dict:
        """

        :param url:  pattern 匹配的正则表达式,
        :param timeout: 默认30秒
        :return: 返回结果
        """
        with self.page.expect_response(lambda response: re.search(url, response.url) and response.status == 200,
                                       timeout=timeout * 1000) as response_info:
            logging.debug("Device %s fetch url %s " % (self.host, response_info.value.url))
        logging.info("Device %s the api response is  %s " % (self.host, response_info.value.json()))
        return response_info.value.json()

    @allure.step('进入菜单')
    def access_menu(self, menu: str, wait_time=None) -> None:
        """进入菜单，多个菜单使用点号隔开，不限多少层级   menu_locator 存放在 base_locators 里面，
            定义menu = {'system': {'locator': '#menu_id', 'wait_locator': '#wait_locator_id'},
                               'status':{'locator': '#status_id', 'wait_locator': '#wait_locator_id'}}
            定义菜单时所有菜单的点号都需要省略，如2.4g 写成24g；空格写成下划线，如wi-fi 2.4g 写成wi-fi_24g
            中划线写成下划线，如wi-fi-2.4g 写成wi_fi_24g


        :param menu: 'system'| 'system.status' 菜单名称全部来自与设备的英文版本，点号需要省略不写， 其他不变，大小写均可以
                     菜单中原有的点号都需要忽略，如wi-fi 2.4g 需要传入wi-fi_24g 或 wi-fi 2.4g 或 wi-fi_2.4g
        :param wait_time: 当操作完菜单后是否需要等待时间 单位毫秒
        :return:
        """

        def in_current_menu(locators: dict) -> bool:
            _in_current_menu = False
            if locators.get('visible_locator'):
                _in_current_menu = True
                for visible_locator in locators.get('visible_locator'):
                    if not visible_locator.is_visible():
                        _in_current_menu = False
                        break
            if _in_current_menu:
                if locators.get('attributes'):
                    for locator, value in locators.get('attributes').items():
                        if locator.is_visible():
                            for attr, expect_value in value.items():
                                if expect_value not in locator.get_attribute(attr):
                                    _in_current_menu = False
                                    break
                            else:
                                _in_current_menu = True
                                continue
                            break
                        else:
                            _in_current_menu = False
                            break
            return _in_current_menu

        def access_one_menu(menu_one: str, locators: dict, level: int):  # 进入某一个菜单
            if not in_current_menu(locators):
                menus = locators.get('menu') if isinstance(locators.get('menu'), list) else [locators.get('menu')]
                for menu_1 in menus:
                    self.click(menu_1)
                logging.info(f'select {level} level menu {menu_one}')
                if locators.get('mouse_move'):
                    self.page.mouse.move(locators.get('mouse_move')[0], locators.get('mouse_move')[1])
                if locators.get('wait_locator'):
                    for wait_locator in locators.get('wait_locator'):
                        wait_locator.wait_for(state='visible')
                    self.page.wait_for_timeout(500)  # 多等500ms
                else:
                    self.page.wait_for_timeout(1000)

        def access(menus):  # 递归进入菜单
            new_menus = []
            click_menus = []
            menu_content = self.content_locator
            # 把菜单名、菜单的元素信息、以及菜单等级依次放入列表中
            for menu_s, level_ in zip(menus, range(1, len(menus) + 1)):
                menu_content = menu_content.get(menu_s)
                new_menus.append([menu_s, menu_content, level_])
            new_menus.reverse()  # 逆序查看是否在当前这个菜单的页面
            for menu_one, locators, level_ in new_menus:
                if not in_current_menu(locators):
                    # 找出需要点击的菜单
                    click_menus.append((menu_one, locators, level_))
                else:
                    break
            if click_menus:
                click_menus.reverse()  # 回归原来的顺序
                for menu_one, locators, level_ in click_menus:
                    access_one_menu(menu_one, locators, level_)
            else:
                logging.debug(f'already in {".".join(menu)} menu')

        def default_change(menu_old, locators: dict) -> str:
            menu_old_s = menu_old.split('.')
            for menu_old_ in menu_old_s:
                locators = locators.get(menu_old_)
            default = locators.get('default')
            menu_new = menu_old + '.' + default if default else menu_old
            return menu_new

        if menu:
            if self.bring_to_front:
                self.page.bring_to_front()
            self.login()
            try:
                menu = menu.replace(' ', '_').replace('-', '_').lower()
                menu = default_change(menu, self.content_locator).split('.')
                access(menu)
            except Exception:
                logging.exception(f'not support this menu {menu}')
                raise f'not support this menu {menu}'
            if wait_time:
                self.page.wait_for_timeout(wait_time)

    @allure.step('输入信息')
    def fill(self, locator: Locator, value: str or int, log_desc=None, force=False) -> None:
        """ 封装公共的输入操作

        :param locator:  元素定位

        :param value: 输入的值
        :param log_desc: 功能描述，用英文 如 Static Routing Destination
        :param force: 强制写入
        :return:
        """
        if value is not None:
            locator.clear()
            locator.fill(str(value), force=force)
            locator.blur()  # 鼠标移出输入框
            if log_desc:
                logging.info(f'Device {self.host} fill {log_desc} {value}')

    @allure.step('点击按钮')
    def click(self, locator: Locator or list or tuple, log_desc=None, dialog_message: str = None,
              tip_messages: str or list = None, text_messages: str or list = None, wait_for_time: int = None,
              tip_messages_timeout=30) -> None:
        """ 封装公共的点击操作 支持多个元素点击, 对点击最后一次的属性做校验

        :param locator:  元素定位
        :param log_desc: 功能描述，用英文 如 Static Routing Destination
        :param dialog_message: str  点击按钮后有dialog弹出，并且期望对信息做验证， 支持模糊匹配, 点击最后一个元素
        :param tip_messages: str or list 点击后等待该tip出现 再等待tip消失，如果有多个，使用列表传入 内容是正则表达式
                            tip_messages 是支持模糊匹配
                            该项校验 页面元素必须停留时间1秒及更多时间，否则不容易检测到导致报错， 点击最后一个元素
        :param text_messages: str or list 点击后等待该文本内容出现，如果有多个，使用列表传入， 内容是正则表达式
        :param wait_for_time: ms  当做完所有操作后是否需要等待时间， 点击最后一个元素
        :param tip_messages_timeout: 默认30秒， 单位秒
        :return:
        """

        def last_click(last_locator: Locator):
            if not last_locator.is_disabled():
                if dialog_message:
                    self.dialog_massage(last_locator.click, dialog_message)
                else:
                    last_locator.click()
                if log_desc:
                    logging.info(f'Device {self.host} click {log_desc}')
                self.tip_messages(tip_messages, tip_messages_timeout)
                self.text_messages(text_messages, tip_messages_timeout)
                if wait_for_time:
                    self.page.wait_for_timeout(wait_for_time)
            else:
                logging.warning(f'Device {self.host} click {log_desc} is disabled')

        if isinstance(locator, (tuple, list)):
            for locator_ in locator[:-1]:
                locator_.click()
            last_click(locator[-1])
        elif isinstance(locator, Locator):
            last_click(locator)
        else:
            logging.exception(f'locator type error {locator}')
            raise TypeError(f'locator type error {locator}')

    @allure.step('勾选框')
    def check(self, locator: Locator, action='check', log_desc=None, tip_messages: str or list = None) -> None:
        """ 封装公共的单选操作
        :param locator:  元素定位
        :param log_desc: 功能描述，用英文 如 Static Routing Destination
        :param action: 'check'|'uncheck'| None | '是' | 'Yes'
        :param tip_messages: str or list 点击后等待该tip出现 再等待tip消失，如果有多个，使用列表传入
                            tip_messages 是支持模糊匹配
                            该项校验 页面元素必须停留时间1秒及更多时间，否则不容易检测到导致报错
        :return:
        """
        try:
            if action is not None:
                if action in ('check', 'Yes', '是', 'yes', 'enable', True):
                    locator.check()
                else:
                    locator.uncheck()
                if log_desc:
                    logging.info(f'Device {self.host} {log_desc} {action}')
                self.tip_messages(tip_messages)
        except playwright.sync_api.Error:
            pass

    @allure.step('下拉单项选择')
    def select_option(self, locator: Locator, value: str or int, log_desc=None) -> None:
        """ 封装公共的下拉选择操作

        :param locator:  元素定位
        :param value: str or int, 下拉选择option的value属性值、或label
        :param log_desc: 功能描述，用英文 如 Static Routing Destination
        :return:
        """

        def scroll_into_view_action(all_option_: Locator, option_: Locator, times=100):
            select = False
            option_end = None
            for find_time in range(0, times):
                if option_.count() == 1:
                    option_.click()
                    select = True
                    break
                elif option_.count() == 0:
                    if option_end != all_option_.last.inner_text():
                        option_end = all_option_.last.inner_text()
                        all_option_.last.scroll_into_view_if_needed()
                        logging.debug(f'scroll down the scroll bar {find_time + 1} tims')
                    else:
                        logging.debug(f'scroll down the bottom')
                        break
                else:
                    logging.exception(f'found more option elements')
                    raise Exception('found more option elements')
            if not select:
                for find_time in range(0, times):
                    if option_.count() == 1:
                        option_.click()
                        break
                    elif option_.count() == 0:
                        if option_end != all_option_.first.inner_text():
                            option_end = all_option_.first.inner_text()
                            all_option_.first.scroll_into_view_if_needed()
                            logging.debug(f'scroll up the scroll bar {find_time + 1}')
                        else:
                            logging.debug(f'scroll up the top')
                            break
                    else:
                        logging.exception(f'found more option elements')
                        raise Exception('found more option elements')
                else:
                    logging.exception(f'scroll bar too lang, more 100 times')
                    raise Exception('scroll bar too lang, more 100 times')

        if value is not None:
            value = str(value)
            locator.wait_for(state='visible')
            if locator.get_attribute('aria-controls') or locator.locator('.ant-select-selection').get_attribute(
                    'aria-controls'):
                if locator.get_attribute("aria-controls"):  # ER805 设备的下拉选择
                    now_option = locator.locator('../..').locator('.ant-select-selection-item').inner_text()
                    option_p = self.page.locator(f'//div[@id="{locator.get_attribute("aria-controls")}"]').locator(
                        '..').locator('//div[@class="rc-virtual-list-holder-inner"]')
                    option = option_p.locator(f'//div[@title="{value}"]')
                    all_option = option_p.locator('.ant-select-item.ant-select-item-option')
                else:  # IG902 设备的下拉选择
                    now_option = locator.locator(
                        '//div/div/div[@class="ant-select-selection-selected-value"]').inner_text()
                    option_id = locator.locator(".ant-select-selection").get_attribute("aria-controls")
                    all_option = self.page.locator(f'//div[@id="{option_id}"]').locator('//ul[@role="listbox"]/li')
                    option = self.page.locator(f'//div[@id="{option_id}"]').locator(
                        f'//ul[@role="listbox"]/li').get_by_text(value, exact=True)
                if now_option != value:
                    locator.scroll_into_view_if_needed()
                    if not locator.is_editable():
                        locator.click(force=True)
                    else:
                        locator.click()
                    scroll_into_view_action(all_option, option)
            else:  # IR300 等设备的下拉选择
                locator.select_option(value)  # value 可以为label 或者value
                if locator.locator(f'//option[@value="{value}"]').count() == 1:
                    value = locator.locator(f'//option[@value="{value}"]').inner_text()
            if log_desc:
                logging.info(f"Device {self.host} select {log_desc} of {value}")

    @allure.step('下拉多项选择')
    def select_more(self, locator: Locator, value: list or str, log_desc=None) -> None:
        """下拉多项选择

        :param locator: 元素定位
        :param value: 一个或多个选项
        :param log_desc: 功能描述，用英文 如 Static Routing Destination
        :return:
        """
        if value is not None:
            value = [value] if isinstance(value, str) else value
            if 'IG' in self.model:
                # 先找出现有已选择的选项， 如果不是就要取消，如果是就不管，
                already_choices = locator.locator('//li[@class="ant-select-selection__choice"]')
                for i in range(0, already_choices.count()):
                    if already_choices.nth(i).locator('//div[1]').inner_text() in value:
                        value.remove(already_choices.nth(i).locator('//div[1]').inner_text())
                    else:
                        self.click(already_choices.nth(i).locator('//span/i[1]'))
                if value:
                    for i_ in range(0, 3):
                        locator.click()
                        try:
                            option_id = locator.locator(".ant-select-selection").get_attribute("aria-controls")
                            for i in value:
                                option = self.page.locator(f'//div[@id="{option_id}"]').locator(
                                    f'//ul[@role="listbox"]/li').get_by_text(i, exact=True)
                                option.click()
                            break
                        except TimeoutError:
                            logging.error("多选框未选择正常")
                    else:
                        raise

            if log_desc:
                logging.info(f"Device {self.host} select {log_desc} more {value}")

    @allure.step('下拉多层級选择')
    def select_multi(self, locator: Locator, value: str, log_desc=None) -> None:
        """ 封装公共的下拉多級选择, 如 IG902 设备的APP下拉多級选择

        :param locator:  元素定位
        :param value: str 多個需使用点号隔开
        :param log_desc: 功能描述，用英文 如 Static Routing Destination
        :return:
        """
        if locator.locator('//span[@class="ant-cascader-picker-label"]').inner_text() != value.split('.')[-1]:
            locator.click()
            for i in value.split('.'):
                self.page.locator(f'//li[text()="{i}"]').click()
            if log_desc:
                logging.info(f"Device {self.host} select {log_desc} of {value}")

    @allure.step('切换按钮')
    def switch_button(self, locator: Locator, action: str = 'enable', log_desc=None) -> None:
        """控制通用开关按钮开关， 如拨号的开关

        :param locator:  开关按钮元素
        :param action: enable, disable, None, True, False 可以开启或关闭，但是并没有提交，只是点击了下
        :param log_desc:  开关功能描述
        :return: None
        """
        if action is not None:
            locator.wait_for(state='visible')
            if (isinstance(action, str) and action.lower() == 'enable') or (isinstance(action, bool) and action):
                if locator.get_attribute('aria-checked') == 'false' or not locator.get_attribute('aria-checked'):
                    locator.click(force=True)
                    if log_desc:
                        logging.info(f"Device {self.host} {log_desc} enabled")
            else:
                if locator.get_attribute('aria-checked') == 'false' or not locator.get_attribute('aria-checked'):
                    pass
                else:
                    locator.click(force=True)
                    if log_desc:
                        logging.info(f"Device {self.host} {log_desc} disabled")

    @allure.step('多点选框操作')
    def radio_select(self, locator: Locator, value: str, log_desc=None) -> None:
        """ 当前只有IG和ER的设备有单选框

        :param locator: 在所有label元素的上级div定位
        :param value: 选项的值，注意国际化
        :param log_desc: 选项的描述
        :return:
        """
        if value:
            locator.wait_for(state='visible')
            option = locator.locator(f'//label', has_text=re.compile(value))
            if option.count() == 1:
                if 'ant-radio-wrapper-checked' not in option.get_attribute('class'):
                    option.click(force=True)
                    if log_desc:
                        logging.info(f"Device {self.host} {log_desc} radio select {value}")
                else:
                    if log_desc:
                        logging.debug(f"Device {self.host} {log_desc} radio already select {value}")
            else:
                logging.exception(f'found {value} option {option.count()} elements')
                raise Exception(f'found {value} option {option.count()} elements')

    @allure.step('单点选框操作')
    def radio(self, locator: Locator, value: str, log_desc=None) -> None:
        """ 当前只有IG和ER的设备有单选框

        :param locator: 在所有label元素的上级div定位
        :param value: 选项的值，注意国际化
        :param log_desc: 选项的描述
        :return:
        """
        if value is not None:
            if value in ('check', True, 'true', 'yes'):
                locator.check()
            else:
                locator.uncheck()
            if log_desc is not None:
                logging.debug(f"Device {self.host} {log_desc} radio {value}")

    @allure.step('伸缩按钮')
    def expand(self, left_text: str, action: str = 'expand') -> None:
        """ 伸缩按钮

        :param left_text: 伸缩按钮 左边的文本，需要注意国际化
        :param action: expand|close|None
        :return:
        """
        text_locator = self.page.get_by_text(left_text, exact=True)
        if action is not None:
            text_locator.wait_for(state='visible')
            if text_locator.count() > 1:
                logging.exception(f'found {left_text} {text_locator.count()} elements')
                raise
            else:
                if 'IG' in self.model:  # IG 产品
                    if 'right' in text_locator.locator('..').locator('//i').get_attribute('aria-label'):
                        if action.lower() == 'expand':
                            self.click(text_locator.locator('..'), f'expand {left_text}')
                    else:
                        if action.lower() == 'close':
                            self.click(text_locator.locator('..'), f'closed {left_text}')
                elif 'ER' in self.model:  # ER805
                    locator = self.page.locator(f'svg[data-icon="right"]:right-of(:text-is("{left_text}"))').first
                    if action.lower() == 'expand':
                        if not locator.get_attribute('style'):
                            self.click(locator, f'expand {left_text}')
                    else:
                        if locator.get_attribute('style') == 'transform: rotate(90deg);':
                            self.click(locator, f'closed {left_text}')
                else:
                    logging.exception(f'not support this expand')
                    raise Exception("not support this expand")

    @allure.step('上传文件')
    def upload_file(self, locator: Locator, path_, dialog_massage=None, tip_messages=None) -> None:
        """

        :param locator:
        :param path_:
        :param dialog_massage
        :param tip_messages
        :return:
        """

        def upload():
            if path_:
                if os.path.isfile(path_) and os.path.exists(path_):
                    with self.page.expect_file_chooser() as fc:
                        locator.click()
                    file_chooser = fc.value
                    file_chooser.set_files(path_)
                    logging.info(f'Device {self.host} upload {path_} success')
                else:
                    logging.error(f'{path_} Does Not Exist.')

        if dialog_massage:
            self.dialog_massage(upload, dialog_massage)
        else:
            upload()
        self.tip_messages(tip_messages)

    @allure.step('下载文件')
    def download_file(self, locator: Locator, file_path, file_name=None) -> None:
        """默认为日志路径

        :param locator: 下载按钮元素
        :param file_path: 下载文件的路径, 不需要跟文件名，
        :param file_name: 如果文件名
        :return:
        """
        if file_path is not None:
            if os.path.isdir(file_path) and os.path.exists(file_path):
                if not locator.is_disabled():
                    with self.page.expect_download() as download_info:
                        locator.click()
                    download = download_info.value
                    file_name = download.suggested_filename if file_name is None else file_name
                    download.save_as(path.join(file_path, file_name))
                    logging.info(
                        f'Device {self.host} download {download.suggested_filename} to path {file_path} success')
                else:
                    logging.warning(f'Device {self.host} {locator} is disabled')
            else:
                logging.error(f'{file_path} Does Not Exist.')

    @allure.step('输入时间或日期')
    def fill_date(self, locator: Locator, date: str) -> None:
        """输入时间或日期

        :param locator:
        :param date: 日期，格式为 2020-01-01
        :return:
        """
        self.click(locator)
        if locator.get_attribute('class') == 'ant-calendar-picker':  # date
            locator_ = self.page.locator('.ant-calendar-input')
        else:
            locator_ = self.page.locator('.ant-time-picker-panel-input')
        locator_.fill(date)
        locator_.press('Enter')
        self.page.wait_for_timeout(500)

    @allure.step("校验dialog message")
    def dialog_massage(self, f, message: str = '') -> None:
        """对话框提示进行校验， 使用时需要在base_locator 里面定义dialog_massage 且返回字典数据

        :param f:  是一个操作函数，执行后会有dialog弹窗出现
        :param message: 校验的信息, 支持模糊匹配
        :return:
        """
        if message:
            message = self.locale.get(message) if self.locale.get(message) else message
            with self.page.expect_event('dialog') as dialog_info:
                f()
            assert message in dialog_info.value.message, f'{self.host} assert {message} dialog error'
            logging.info(f'Device {self.host} assert dialog {message} success')

    @allure.step("校验tip messages")
    def tip_messages(self, messages: str or re.Pattern or list = None, timeout=30) -> None:
        """ 某些提交操作会出现文本的提示，提示在过几秒钟后会消失，对于该类消息的验证使用该方法，
            使用时需要在base_locator tip_messages 且返回字典数据

        :param messages: str or re.Pattern  点击后等待该tip出现 再等待tip消失，
                            messages str 是支持模糊匹配 如果有多个，使用列表传入
                            re.compile(message)  支持正则   如果有多个，使用列表传入
                            re.compile(message, re.IGNORECASE) 支持正则忽略大小写  如果有多个，使用列表传入
                            该项校验 页面元素必须停留时间1秒及更多时间，否则不容易检测到导致报错
        :param timeout: 校验超时时间
        :return:
        """
        if messages:
            if isinstance(messages, str):
                tip_messages = [self.locale.get(messages)] if self.locale.get(messages) else [messages]
            elif isinstance(messages, re.Pattern):
                tip_messages = [messages]  # 正则表达式 时需要自己做国际化转换
            elif isinstance(messages, list):
                tip_messages = [self.locale.get(message) if self.locale.get(message) else message for message in
                                messages]
            else:
                raise Exception("messages type error")
            for message in tip_messages:
                expect(self.page.get_by_text(message)).to_be_visible(timeout=timeout * 1000)
                expect(self.page.get_by_text(message)).to_be_hidden(timeout=timeout * 1000)
                logging.info(f'{self.host} assert tip {message} visible success')

    @allure.step("校验text messages")
    def text_messages(self, messages: str or re.Pattern or list = None, timeout=10) -> None:
        """ 对文本内容做验证，如在输入框输入错误内容时出现的文本，该类文本会一直存在
        :param messages: str or re.Pattern
                            messages str 是支持模糊匹配 如果有多个，使用列表传入
                            re.compile(message)  支持正则   如果有多个，使用列表传入
                            re.compile(message, re.IGNORECASE) 支持正则忽略大小写  如果有多个，使用列表传入
        :param timeout: 校验超时时间
        :return:
        """
        if messages:
            if isinstance(messages, str):
                messages = [self.locale.get(messages)] if self.locale.get(messages) else [messages]
            elif isinstance(messages, re.Pattern):
                messages = [messages]  # 正则表达式 时需要自己做国际化转换
            elif isinstance(messages, list):
                messages = [self.locale.get(message) if self.locale.get(message) else message for message in messages]
            else:
                raise Exception("messages type error")
            text_messages = Counter(messages)  # 处理多个相同的文本
            for message, count in text_messages.items():
                for i_ in range(0, count):
                    expect(self.page.get_by_text(message).nth(i_)).to_be_visible(timeout=timeout * 1000)
                    logging.info(f'{self.host} assert text the {i_}th {message}  visible success')

    @allure.step("校验元素Title")
    def title_messages(self, messages: str or re.Pattern or list = None, timeout=10) -> None:
        """ 对元素的属性title做内容验证，
        :param messages: str or re.Pattern
                            messages str 是支持模糊匹配 如果有多个，使用列表传入
                            re.compile(message)  支持正则   如果有多个，使用列表传入
                            re.compile(message, re.IGNORECASE) 支持正则忽略大小写  如果有多个，使用列表传入
        :param timeout: 校验超时时间
        :return:
        """
        if messages:
            if isinstance(messages, str):
                messages = [self.locale.get(messages)] if self.locale.get(messages) else [messages]
            elif isinstance(messages, re.Pattern):
                messages = [messages]  # 正则表达式 时需要自己做国际化转换
            elif isinstance(messages, list):
                messages = [self.locale.get(message) if self.locale.get(message) else message for message in messages]
            else:
                raise Exception("messages type error")
            text_messages = Counter(messages)
            for message, count in text_messages.items():
                for i_ in range(0, count):
                    expect(self.page.get_by_title(message).nth(i_)).to_be_visible(timeout=timeout * 1000)
                    logging.info(f'{self.host} assert title the {i_}th {message} visible success')

    @allure.step('设置页面翻页')
    def page_refresh(self, refresh_time: str, select_locator: Locator) -> None:
        """
        :param refresh_time: str
                        '0'|'3'|'4'|'5'|'10'|'15'|'30'|'60'|'120'|'180'|'240'|'300'|'600'|'900'|'1200'|'1800'
        :param select_locator: 元素定位
        :return:
        """
        # 待完善
        if self.model in ('VG710', 'IR302'):
            if select_locator.evaluate("el => el.value") == str(
                    refresh_time) and select_locator.is_disabled():
                pass
            else:
                if select_locator.is_disabled():
                    self.click(select_locator.locator('..').locator('#refresh-button'), 'refresh button')
                    self.page.wait_for_timeout(500)
                self.select_option(select_locator, refresh_time, 'refresh time select')
                self.click(select_locator.locator('..').locator('#refresh-button'), 'refresh button ok')

    def turn_page(self, father_locator: Locator = None, page_number=1):
        """分页， 指定点到第几页  只有IG 产品拥有该方法

        :param father_locator: 当同一页面存在多个分页时，需要传入父元素定位组合成链式定位，确认唯一
        :param page_number: 第几页
        :return: 找不到页数时返回False
        """
        if self.model in ('IG902', 'IG502'):
            locator = self.page.locator(f'.ant-pagination-item-{page_number}')
            if father_locator:
                locator = father_locator.locator(f'.ant-pagination-item-{page_number}')
            if locator.is_visible():
                self.click(locator, f'turn page {page_number}', wait_for_time=500)
                return True
            else:
                return False
        else:
            raise Exception(f'{self.model} not support turn page')

    @allure.step("操作表格")
    def table_tr(self, locators: dict, value: list, log_desc=None) -> List[int or None] or None:
        """

        :param locators: {"locator": $locator2, "param": {$key2: $value2}, "columns": list, 'unique_columns': list}
        :param value: [($action,{**kwarg})] ex: [('delete_all', )],  [('edit', $old, $new)]多个操作时使用列表 [('add',{}), ('add',{})]
        :param log_desc: 日志描述
        :return:
        """
        if self.model in ('IG902', 'IG502'):
            tr = IgTable(locators.get('columns'), locators.get('locator'), locators.get('param'), log_desc,
                         locators.get('action_confirm'), locators.get('pop_up_locator'))
            exist_tr = []
            if value:
                for value_ in value:
                    if value_[0] in ('add', 'install'):
                        tr.add(self.agg_in, **value_[1])
                        if value_[0] == 'install':  # app 的安装，安装完成页面要重新加载，需要固定等点时间
                            self.page.wait_for_timeout(5000)
                    elif value_[0] == 'delete_all':
                        tr.delete_all()
                    elif value_[0] in ('delete', 'uninstall'):
                        tr.delete(value_[1])
                    elif value_[0] == 'exist':
                        exist_tr.append(tr.exist(value_[1], self.locale))
                    elif value_[0] == 'edit':
                        tr.edit(self.agg_in, value_[1], **value_[2])
                    elif value_[0] == 'connect':
                        tr.connect(value_[1])
                    elif value_[0] == 'associate_delete':
                        tr.associate_delete(value_[1])
                    elif value_[0] in ('download_log', 'export_config', 'export_historical_data'):
                        if isinstance(value_[2], str):
                            file_path = value_[2]
                            file_name = None
                        elif isinstance(value_[2], dict):
                            file_path = value_[2].get('file_path')
                            file_name = value_[2].get('file_name')
                        else:
                            logging.exception('download file_path type error')
                            raise TypeError('download file_path type error')
                        tr.download(self.download_file, value_[1], file_path, file_name)
                    elif value_[0] in ('upload', 'import_config'):
                        tr.upload(self.upload_file, value_[1], value_[2])
                    elif value_[0] == 'start':
                        tr.start(value_[1])
                    elif value_[0] == 'stop':
                        tr.stop(value_[1])
                    elif value_[0] == 'restart':
                        tr.restart(value_[1])
                    elif value_[0] in ('check', 'enable'):
                        tr.check(self.check, value_[1], value_[2])
                    elif value_[0] == 'clear_log':
                        tr.clear_log(value_[1])
                    elif value_[0] == 'clear_historical_data':
                        tr.clear_historical_data(value_[1])
                return exist_tr
        else:
            tr = Table(locators.get('columns'), locators.get('locator'),
                       locators.get('unique_columns'), locators.get('param'), log_desc)
            exist_tr = []
            if value:
                for value_ in value:
                    if value_[0] == 'add':
                        tr.add(**value[1])
                    elif value_[0] == 'delete_all':
                        tr.delete_all()
                    elif value_[0] == 'delete':
                        tr.delete(**value[1])
                    elif value_[0] == 'exist':
                        exist_tr.append(tr.exist(**value[1]))
                    elif value_[0] == 'edit':
                        tr.edit(value[1], value[2])
                return exist_tr

    def monaco(self, locator: Locator, value: str, log_desc=None):
        """慕尼黑编辑器输入

        :param locator:
        :param value: 换行需要使用\n
        :param log_desc:
        :return:
        """
        self.click(locator, )
        self.page.keyboard.press('Control+A')
        self.page.keyboard.press('Delete')
        self.page.keyboard.type(value)
        logging.info(f'{log_desc} monaco-editor：{value}')

    def value_mapping(self, locator, value: tuple or list):
        """ 目前只有IG產品有

        :param locator:
        :param value:
        :return:
        """
        for i in range(0, locator.get('table').locator('//tbody/tr').count()):
            self.click(locator.get('table').locator('//tbody/tr').nth(0).locator('//td[3]/a'))
            self.click(locator.get('ok'))
            self.page.wait_for_timeout(1000)
        for i in range(0, len(value)):
            self.click(locator.get('add'))
            self.fill(locator.get('table').locator('//tbody/tr').nth(i).locator('//td[1]').locator('//input'),
                      value[i][0])
            self.fill(locator.get('table').locator('//tbody/tr').nth(i).locator('//td[2]').locator('//input'),
                      value[i][1])
            self.page.wait_for_timeout(500)

    def agg_in(self, locators: list, action_dict: dict) -> None:
        """封装公共的整合输入操作
                :param locators:  列表 嵌套 长度为2的元组，元组的第一项为操作项名称， 第二项为对应的一个字典
                    [($param1, {"locator": $locator1, "type": $type1, "relation": [($param2, $value2)], "param": {$key1: $value1}}),
                    ($param2, {"locator": $locator2, "type": $type2, "relation": [($param3, $value3),……], "param": {$key2: $value2}}),
                    ($param3, {"locator": $locator2, "type": 'table_tr', "relation": [($param3, $value3),……], "param": {$key2: $value2},
                                "columns": list, 'unique_columns': list}),]
                    $param: 操作项的名称，如 'language'|'sim'|'status'
                    $locator: 操作项的元素定位， locator or [locator,locator,...]
                    $type: 操作项的类型 text|select|select_multi|select_more|button|check|upload_file|download_file|tip_messages|text_messages|title_messages|fill_date|
                                     multi_select|multi_check|multi_fill|table_tr|switch_button|radio_select|expand|monaco|value_mapping
                            select value值可以是label|Value
                            multi_select指一个参数有多个select, 对应操作项的多个locator及value用[]传入
                    "relation":[($param, $value)]: 操作项的关联项，若有多个则首个为最先操作的关联项，其中$param为关联项的名称，$value为关联项的预期值
                    "param":{$key, $value}: 参数转换，如大小写转换{"ab":"AB"} {"wan":"Wan"}等.
                    "always_do": True|False: 操作项是否必须操作, 哪怕是报异常也会做
                :param action_dict: 要做操作的参数名称与对应的值{$param1: $value1, $param2: $value2}
                :return:
                """
        relations = []

        def operation(param, param_locator, value):
            if param_locator.get('type') == 'text':
                self.fill(param_locator.get('locator'), value, param)
            elif param_locator.get('type') == 'monaco':
                self.monaco(param_locator.get('locator'), value, param)
            elif param_locator.get('type') == 'select':
                if param_locator.get('param'):
                    value = param_locator.get('param').get(value) if param_locator.get('param').get(value) else value
                self.select_option(param_locator.get('locator'), value, param)
            elif param_locator.get('type') == 'select_more':
                if param_locator.get('param'):
                    value = param_locator.get('param').get(value) if param_locator.get('param').get(value) else value
                self.select_more(param_locator.get('locator'), value, param)
            elif param_locator.get('type') == 'select_multi':
                if param_locator.get('param'):
                    value = param_locator.get('param').get(value) if param_locator.get('param').get(value) else value
                self.select_multi(param_locator.get('locator'), value, param)
            elif param_locator.get('type') == 'radio_select':
                if param_locator.get('param') and value in param_locator.get('param').keys():
                    value = param_locator.get('param').get(value)
                self.radio_select(param_locator.get('locator'), value, param)
            elif param_locator.get('type') == 'radio':
                if param_locator.get('param') and value in param_locator.get('param').keys():
                    value = param_locator.get('param').get(value)
                self.radio(param_locator.get('locator'), value, param)
            elif param_locator.get('type') == 'switch_button':
                self.switch_button(param_locator.get('locator'), value, param)
            elif param_locator.get('type') == 'expand':
                self.expand(param_locator.get('locator'), value)  # 此处获取到的locator 是一个str
            elif param_locator.get('type') == 'button':
                if value:
                    dialog_message, tip_messages, wait_for_time, text_messages, tip_messages_timeout = None, None, None, None, 30
                    if isinstance(value, dict):
                        dialog_message = value.get('dialog_message')
                        tip_messages = value.get('tip_messages')
                        wait_for_time = value.get('wait_for_time')
                        text_messages = value.get('text_messages')
                        tip_messages_timeout = value.get('tip_messages_timeout') if value.get(
                            'tip_messages_timeout') is not None else 30
                    self.click(param_locator.get('locator'), param, dialog_message, tip_messages, text_messages,
                               wait_for_time, tip_messages_timeout)
            elif param_locator.get('type') == 'check':
                if value:
                    value_, tip_messages = value, None
                    if isinstance(value, dict):
                        value_ = value.get('value')
                        tip_messages = value.get('tip_messages')
                    self.check(param_locator.get('locator'), value_, param, tip_messages)
            elif param_locator.get('type') == 'table_tr':
                if isinstance(value, list):  # value按照table_tr()的传参方式传参,
                    self.table_tr(param_locator.get('locator'), value, param)
                else:
                    logging.error(f'value {value} should be a list, not {type(value)}')
            elif param_locator.get('type').startswith('multi_'):
                if len(param_locator.get('locator')) == len(value):
                    for locator_, value_ in dict(zip(param_locator.get('locator'), value)):
                        if 'select' in param_locator.get('type'):
                            if param_locator.get('param') and value_ in param_locator.get('param').keys():
                                value_ = param_locator.get('param').get(value_)
                            self.select_option(locator_, value_, param)
                        elif param_locator.get('type').endswith('check'):
                            self.check(locator_, value_, param)
                        elif param_locator.get('type').endswith('fill'):
                            self.fill(locator_, value_, param)
                        else:
                            logging.error(f"not support this param type {param_locator.get('type')}")
                else:
                    logging.error('Wrong length or type of locator or value!')
            elif param_locator.get('type') == 'upload_file':
                if value:
                    file_path, dialog_message, tip_message = value, None, None
                    if isinstance(value, dict):
                        file_path, dialog_message, tip_message = value.get('file_path'), value.get(
                            'dialog_message'), value.get('tip_messages')
                    elif isinstance(value, str):
                        pass
                    self.upload_file(param_locator.get('locator'), file_path, dialog_message, tip_message)
            elif param_locator.get('type') == 'download_file':
                if value:
                    file_path, file_name = value, None
                    if isinstance(value, dict):
                        file_path, file_name = value.get('file_path'), value.get('file_name')
                    elif isinstance(value, str):
                        pass
                    self.download_file(param_locator.get('locator'), file_path, file_name)
            elif param_locator.get('type') == 'tip_messages':
                if value:
                    messages, timeout = value, 10
                    if isinstance(value, dict):
                        timeout = value.get('timeout') if value.get('timeout') else 10
                        messages = value.get('messages')
                    self.tip_messages(messages, timeout)
            elif param_locator.get('type') == 'text_messages':  # 用逗号分解多个
                if value:
                    messages, timeout = value, 10
                    if isinstance(value, dict):
                        timeout = value.get('timeout') if value.get('timeout') else 10
                        messages = value.get('messages')
                    self.text_messages(messages, timeout)
            elif param_locator.get('type') == 'title_messages':
                if value:
                    messages, timeout = value, 10
                    if isinstance(value, dict):
                        timeout = value.get('timeout') if value.get('timeout') else 10
                        messages = value.get('messages')
                    self.title_messages(messages, timeout)
            elif param_locator.get('type') == 'fill_date':
                self.fill_date(param_locator.get('locator'), value)
            elif param_locator.get('type') == 'value_mapping':
                self.value_mapping(param_locator.get('locator'), value)
            else:
                logging.exception(f"not support this param type {param_locator.get('type')}")
                raise Exception(f"not support this param type {param_locator.get('type')}")
            if param_locator.get('wait_for'):
                wait_for = [param_locator.get('wait_for')] if isinstance(param_locator.get('wait_for'),
                                                                         dict) else param_locator.get('wait_for')
                for wait_for_ in wait_for:
                    if wait_for_.get('type') == 'timeout':
                        self.page.wait_for_timeout(wait_for_.get('timeout'))
                    elif wait_for_.get('type') == 'visible':
                        wait_for_.get('locator').wait_for(state='visible', timeout=wait_for_.get('timeout'))
                    elif wait_for_.get('type') == 'hidden':
                        wait_for_.get('locator').wait_for(state='hidden', timeout=wait_for_.get('timeout'))
                    elif wait_for_.get('type') == 'tip_messages':
                        timeout = wait_for_.get('timeout') if wait_for_.get('timeout') else 30
                        self.tip_messages(wait_for_.get('messages'), timeout)
            if param_locator.get('mouse_move'):
                self.page.mouse.move(param_locator.get('mouse_move')[0], param_locator.get('mouse_move')[1])

        if action_dict:
            always_do_value = None
            always_do_all = [(option[0], option[1]) for option in locators if
                             isinstance(option[1], dict) and option[1].get("always_do")]
            if len(always_do_all) >= 1 and action_dict.get(always_do_all[0][0]) is not None:  # always_do 始终要做的操作
                always_do_value = action_dict.pop(always_do_all[0][0])
            try:
                for option in locators:
                    assert type(option) in (tuple, list) and len(option) == 2, "type of option is incorrect"
                    if option[0] in [key for key, value in action_dict.items() if value is not None]:
                        if isinstance(option[1], dict):
                            if option[1].get("relation") and option[1].get("relation") not in relations:
                                # 对关系项操作之前检查关系项
                                for relation_ in option[1].get("relation"):
                                    relation_locator = [i[1] for i in locators if i[0] == relation_[0]][0]
                                    operation(relation_[0], relation_locator, relation_[1])  # 关系项操作
                                relations.append(option[1].get("relation"))
                            operation(option[0], option[1], action_dict.get(option[0]))  # 本身操作
                        elif isinstance(option[1], list) and isinstance(action_dict.get(option[0]),
                                                                        list):  # 当使用一个变量传多个元素的值时
                            for option_, action_value in zip(option[1], action_dict.get(option[0])):
                                if option_.get("relation") and option_.get("relation") not in relations:
                                    # 对关系项操作之前检查关系项
                                    for relation_ in option_.get("relation"):
                                        relation_locator = [i[1] for i in locators if i[0] == relation_[0]][0]
                                        operation(relation_[0], relation_locator, relation_[1])  # 关系项操作
                                    relations.append(option_.get("relation"))
                                operation(option[0], option_, action_value)  # 本身操作
                        else:
                            logging.exception("type of option is incorrect")
                            raise Exception("type of option is incorrect")
            except Exception as e:
                raise e
            finally:
                if always_do_value is not None:
                    operation(always_do_all[0][0], always_do_all[0][1], always_do_value)

    @allure.step("计算元素表达式")
    def eval_locator_attribute(self, expect_: dict, locators: list) -> bool:
        """对页面特定元素值做判断

        :param expect_: {$status: $expressions}
                        status: 状态名称， 比如可以传定义好的 current_sim
                        expressions: 完整表达式, 当判断int型的关系时${value}和期望值可加"",而当需要调用str型的关系时${value}和期望值都要加"",
                         例:（'${value}==1', '${value}!=1', '${value}>1', '${value}>=1', '${value}<1', '${value}<=1', "${value}"=="abc"
                        '"${value}".startswith("123")', '"${value}".endswith("23")', '"${value}" in a', '"${value}" not in b',
                        '"${value}".__contains__("234")', 'time.strptime("${value}}", "%Y-%m-%d %H:%M:%S")'）
                        ex: '${value}==8' 多个使用元组或者列表，注意期望值是字符串时需要带上引号， 如'${value}=="sim1"'
        :param locators: [($param1, {"locator": $locator1, "type": $type1, "relation": [($param2, $value2)], "param": {$key1: $value1}}),
                          ($param2, {"locator": $locator2, "type": $type2, "relation": [($param3, $value3),……], "param": {$key2: $value2}}),
                          ($param3, {"locator": $locator2, "type": 'table_tr', "relation": [($param3, $value3),……], "param": {$key2: $value2},
                                "columns": list, 'unique_columns': list}),]
                          type:  text, switch_button, fill

        :return: 只返回True or False 不做断言
        """
        if expect_:
            for key in expect_.keys():
                filter_key = list(filter(lambda x: x[0] == key, locators))
                if len(filter_key) == 1:
                    option = filter_key[0]
                    locator = option[1].get('locator')
                    if isinstance(locator, Locator):
                        if locator.count() != 0:
                            if option[1].get('type') == 'switch_button':
                                if 'ant-switch-checked' in locator.first.get_attribute('class'):
                                    value = 'enable'
                                else:
                                    value = 'disable'
                            elif option[1].get('type') == 'fill':
                                value = locator.first.input_value()
                            elif option[1].get('type') == 'class':
                                value = locator.first.get_attribute('class')
                            else:  # type is text
                                value = locator.first.inner_text()
                        else:
                            value = None
                    else:
                        value = str(locator)
                    try:
                        if isinstance(expect_.get(key), str) and '${value}' in expect_.get(key):
                            expression = expect_.get(key).replace('${value}', value).replace('\n', ' ')
                            if option[1].get('param'):
                                expression = replace_str(expression, option[1].get('param'))
                            log_expression = expression
                            logging.info(f'assert {expression}')
                        else:
                            ex_ = expect_.get(key)
                            if option[1].get('param') and isinstance(ex_, str):
                                ex_ = replace_str(expect_.get(key), option[1].get('param'))
                            log_expression = f'{ex_} == {value}'  # 默认使用等于判断
                            ex_ = f'"{base64.b64encode(ex_.encode())}"' if isinstance(ex_, str) else ex_
                            value = f'"{base64.b64encode(value.encode())}"' if isinstance(value, str) else value
                            expression = f'{ex_} == {value}'
                        if eval(expression):
                            logging.info(f'assert {log_expression} is success')
                        else:
                            logging.info(f'assert {log_expression} is failed')
                            return False
                    except TypeError:
                        logging.error(f'get {key} inner_text failed')
                        return False
        return True

    @allure.step("获取页面元素文本值")
    def get_text(self, keys: str or list or tuple, locators: list) -> str or dict or None:
        """获取页面元素文本值

        :param keys: None or str or list or tuple, 需要获取对应文本的元素的关键字
        :param locators: [($param1, {"locator": $locator1, "type": $type1}),
                         type: 支持的类型有：'text'|'fill'|'select'|'clipboard'|'switch_button'
                         该select 为select标签的文本值， ER805 和ER605 直接使用text
        :return: 当key为None时，返回None
                 当key为str时，只能获取某一个字段的信息，同时使用str返回
                 当key为列表或者元组时， 使用字典返回相关关键字的信息
        """
        result = {}
        if keys:
            keys = [keys] if isinstance(keys, str) else keys
            for key in keys:
                filter_key = list(filter(lambda x: x[0] == key, locators))
                if len(filter_key) == 1:
                    option = filter_key[0]
                    locator = option[1].get('locator')
                    if isinstance(locator, Locator):
                        if locator.count() != 0:
                            if option[1].get('type') == 'select':
                                value = locator.first.text_content()
                            elif option[1].get('type') == 'fill':
                                value = locator.first.input_value()
                            elif option[1].get('type') == 'clipboard':
                                locator.first.click()
                                value = self.page.evaluate('navigator.clipboard.readText()')
                            elif option[1].get('type') == 'switch_button':
                                if 'ant-switch-checked' in locator.first.get_attribute('class'):
                                    value = 'enable'
                                else:
                                    value = 'disable'
                            elif option[1].get('type') == 'class':
                                value = locator.first.get_attribute('class')
                            else:
                                value = locator.first.inner_text()
                        else:
                            value = None
                    else:
                        value = str(locator)
                    result[key] = value
                else:
                    logging.exception(f'not support the key {key}')
                    raise KeyError(f'not support the key {key}')
        if result:
            if len(result.keys()) == 1:
                return result.get(keys[0])
            else:
                return result
        else:
            return None

    @allure.step("PC Ping")
    def pc_ping(self, host_or_ip: str or list or tuple = 'www.baidu.com', number: int = 4, src=None,
                lost_packets=False, assert_result=True, timeout=120, interval=10) -> None:
        """ 验证在PC机上ping某个地址是否丢包， 仅判断丢包

        :param lost_packets:
        :param src: 验证的源IP地址 '192.168.2.100'
        :param host_or_ip: 验证的目的IP地址, 可使用元组或列表接收多个地址
        :param number: 包数量
        :param lost_packets: True|False 如果为True判断会丢包，如果为False判断不丢包
        :param assert_result: True|False 是否对 lost_packets 的结果做判断
        :param timeout: 超时时间
        :param interval: 间隔时间
        :return:
        """
        from inhandtest.tools import pc_ping
        pc_ping(host_or_ip, number, src, lost_packets, assert_result, timeout, interval)

    def close(self) -> None:
        if self.__context and self.__browser and self.__playwright:
            self.__context.close()
            self.__browser.close()
            self.__playwright.stop()
            logging.info('close browser and playwright')


if __name__ == '__main__':
    pass
