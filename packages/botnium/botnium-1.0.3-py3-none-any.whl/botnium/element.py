__version__ = "1.0.1"

import datetime
from datetime import timedelta
from typing import Literal, Union
from clicknium import clicknium as cc, locator, ui
from sqlalchemy import literal
from botnium import logger
from botnium.common import remove_file_if_exists
from botnium.common.models import RpaException
from time import sleep
import botnium
from clicknium.common.enums import *


def wait_appear(
    _locator,
    locator_variables: dict = {},
    wait_timeout: int = 30
    ):
    logger.logger.logger.debug('开始等待元素出现 - {}'.format(str(_locator)))
    result = cc.wait_appear(_locator, locator_variables, wait_timeout)
    logger.logger.debug('结束等待元素出现 - {}，是否存在：{}'.format(str(_locator), ('是' if result else '否')))
    return result

def click(
        _locator,
        locator_variables: dict = {},
        mouse_button: Literal["left", "middle", "right"] = MouseButton.Left,
        by: Literal["default", "mouse-emulation", "control-invocation"] = MouseActionBy.Default,
        modifier_key: Literal["nonekey", "alt", "ctrl", "shift","win"]  = ModifierKey.NoneKey,
        window_mode: Literal["auto", "topmost", "noaction"] = WindowMode.Auto,
        timeout: int = 30
    ) -> None:
    try:
        logger.logger.debug('开始点击元素 - {}'.format(str(_locator)))
        cc.find_element(_locator, locator_variables, window_mode).click(mouse_button=mouse_button, by=by, modifier_key=modifier_key, timeout= timeout)
        logger.logger.debug('结束元素点击 - {}'.format(str(_locator)))
        pass
    except:
        raise RpaException('点击{}失败，元素不存在'.format(str(_locator)))
    
def try_click(
        _locator,
        locator_variables: dict = {},
        mouse_button: Literal["left", "middle", "right"] = MouseButton.Left,
        by: Literal["default", "mouse-emulation", "control-invocation"] = MouseActionBy.Default,
        modifier_key: Literal["nonekey", "alt", "ctrl", "shift","win"]  = ModifierKey.NoneKey,
        window_mode: Literal["auto", "topmost", "noaction"] = WindowMode.Auto,
        wait_timeout: int = 15,
        timeout: int = 30
    ) -> bool:
    ele = wait_appear(_locator, locator_variables, wait_timeout=wait_timeout)
    if ele:
        logger.logger.debug('开始点击元素 - {}'.format(str(_locator)))
        cc.find_element(_locator, locator_variables, window_mode).click(mouse_button=mouse_button, by=by, modifier_key=modifier_key, timeout= timeout)
        logger.logger.debug('结束元素点击 - {}'.format(str(_locator)))
        sleep(2)
        return True
    else:
        logger.logger.debug('元素不存在，忽略点击')
        return False

def is_existing(
        _locator,
        locator_variables: dict = {},
        timeout: int = 30
    ) -> bool:
    logger.logger.debug('开始检查元素是否存在 - {}'.format(str(_locator)))
    result = cc.is_existing(_locator, locator_variables, timeout)
    logger.logger.debug('结束检查元素是否存在 - {}, 是否存在：{}'.format(str(_locator), result))
    return result


def element_existing(page, selector, timeout=30000):
    try:
        page.wait_for_selector(selector, timeout=timeout)
        return True
    except:
        return False
    
def save_or_open_file(targetPath, sleepSeconds = 5, title = '已完成*'):
    try:
        nameDict = { 'name': title}
        cc.wait_appear(locator.common.a360se.text_你要打开还是保存此文件, nameDict)
        ui(locator.common.a360se.text_你要打开还是保存此文件, nameDict).click()
        sleep(1)
        cc.send_hotkey('%S')  # Alt + S 保存
        sleep(2)
        cc.send_hotkey('{DEL}')
        sleep(1)
        ui(locator.common.a360se.edit_文件名, nameDict).set_text(targetPath, by='set-text')
        sleep(1)
        remove_file_if_exists(targetPath)
        ui(locator.common.a360se.button_保存s, nameDict).click(by='control-invocation')
        sleep(sleepSeconds)
        pass
    except:
        raise RpaException('下载失败 - 请确认保存框是否弹出')

'''chrome浏览器设置Element 日期选择器'''
def set_ele_date_range(title, locator_n, start_date: str, end_date: str):
    cc.find_element(locator_n).click(by='mouse-emulation')
    sleep(1)
    startDate = datetime.strptime(start_date, '%Y-%m-%d')
    startMonth = startDate - timedelta(days=startDate.day - 1)
    endDate = datetime.strptime(end_date, '%Y-%m-%d')
    endMonth = endDate - timedelta(days=endDate.day - 1)
    titlePara = {'title': title}
    displayLeftMonthStr = ui(locator.common.ele.datepicker_left_header, titlePara).get_text().replace(' ', '').replace('年', '-').replace('月', '')
    displayLeftMonth = datetime.strptime(displayLeftMonthStr, '%Y-%m')
    while displayLeftMonth > startMonth:
        ui(locator.common.ele.button_el_picker_arrow_left, titlePara).click()
        sleep(2)
        displayLeftMonthStr = ui(locator.common.ele.datepicker_left_header, titlePara).get_text().replace(' ', '').replace('年', '-').replace('月', '')
        displayLeftMonth = datetime.strptime(displayLeftMonthStr, '%Y-%m')
        pass
    while displayLeftMonth < startMonth:
        ui(locator.common.ele.button_el_picker_arrow_right, titlePara).click()
        sleep(2)
        displayLeftMonthStr = ui(locator.common.ele.datepicker_left_header, titlePara).get_text().replace(' ', '').replace('年', '-').replace('月', '')
        displayLeftMonth = datetime.strptime(displayLeftMonthStr, '%Y-%m')
        pass
    dayDict = {'day': startDate.day, 'title': title}
    ui(locator.common.ele.button_el_picker_left_day, dayDict).click(by='mouse-emulation')
    sleep(2)
    if startMonth == endMonth:
        dayDict = {'day': endDate.day, 'title': title}
        ui(locator.common.ele.button_el_picker_left_day, dayDict).click(by='mouse-emulation')
        sleep(2)
    else:
        displayRightMonthStr = ui(locator.common.ele.datepicker_right_header, titlePara).get_text().replace(' ', '').replace('年', '-').replace('月', '')
        displayRightMonth = datetime.strptime(displayRightMonthStr, '%Y-%m')
        while displayRightMonth > endMonth:
            ui(locator.common.ele.button_el_picker_arrow_left, titlePara).click()
            sleep(1)
            displayRightMonthStr = ui(locator.common.ele.datepicker_right_header, titlePara).get_text().replace(' ', '').replace('年', '-').replace('月', '')
            displayRightMonth = datetime.strptime(displayRightMonthStr, '%Y-%m')
            pass
        while displayRightMonth < endMonth and displayRightMonth.year != endDate.year and displayRightMonth.month != endDate.month:
            ui(locator.common.ele.button_el_picker_arrow_right, titlePara).click()
            sleep(1)
            displayRightMonthStr = ui(locator.common.ele.datepicker_right_header, titlePara).get_text().replace(' ', '').replace('年', '-').replace('月', '')
            displayRightMonth = datetime.strptime(displayRightMonthStr, '%Y-%m')
            pass
        dayDict = {'day': endDate.day, 'title': title}
        ui(locator.common.ele.button_el_picker_right_day, dayDict).click(by='mouse-emulation')
        sleep(2)
    pass