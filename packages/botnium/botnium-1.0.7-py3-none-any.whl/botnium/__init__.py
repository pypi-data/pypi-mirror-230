__version__ = "1.0.7"

import datetime
from datetime import timedelta, datetime
from typing import Literal, Union, List
from clicknium import clicknium as cc, locator, ui
from sqlalchemy import literal
from botnium import logger
from botnium.common import remove_file_if_exists
from botnium.common.models import RpaException
from time import sleep
import botnium
from clicknium.common.enums import *
from clicknium.core.models.uielement import UiElement
from clicknium.locator import _Locator

def wait_appear(
    _locator,
    locator_variables: dict = {},
    wait_timeout: int = 30
    ):
    logger.logger.debug('开始等待元素出现 - {}'.format(str(_locator)))
    result = cc.wait_appear(_locator, locator_variables, wait_timeout)
    logger.logger.debug('结束等待元素出现 - {}，是否存在：{}'.format(str(_locator), ('是' if result else '否')))
    return result

def wait_disappear(
    _locator,
    locator_variables: dict = {},
    wait_timeout: int = 30
    ):
    logger.logger.debug('开始等待元素消失 - {}'.format(str(_locator)))
    exists = cc.is_existing(_locator, locator_variables, timeout=10)
    retryTimes = 1
    while exists and retryTimes * 10 < wait_timeout:
        exists = cc.is_existing(_locator, locator_variables, timeout=10)
        retryTimes += 1
        pass
    logger.logger.debug('结束等待元素消失 - {}，是否存在：{}'.format(str(_locator), ('是' if exists else '否')))
    if exists:
        raise RpaException('等待元素{}消失失败'.format(_locator))
    
def click(
        _locator,
        locator_variables: dict = {},
        mouse_button: Literal["left", "middle", "right"] = MouseButton.Left,
        by: Literal["default", "mouse-emulation", "control-invocation"] = MouseActionBy.Default,
        modifier_key: Literal["nonekey", "alt", "ctrl", "shift","win"]  = ModifierKey.NoneKey,
        window_mode: Literal["auto", "topmost", "noaction"] = WindowMode.Auto,
        timeout: int = 30,
        sleepSeconds: int = 2
    ) -> None:
    try:
        logger.logger.debug('开始点击元素 - {}'.format(str(_locator)))
        cc.find_element(_locator, locator_variables, window_mode).click(mouse_button=mouse_button, by=by, modifier_key=modifier_key, timeout= timeout)
        logger.logger.debug('结束元素点击 - {}'.format(str(_locator)))
        sleep(sleepSeconds)
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
        timeout: int = 30,
        sleepSeconds: int = 2,
        try_times: int = 1
    ) -> bool:
    retry_index = 0
    ele = None
    while retry_index < try_times:
        if try_times > 1:
             logger.logger.debug('第 {}/{} 尝试点击'.format(str(retry_index+1), str(try_times)))
             pass
        ele = wait_appear(_locator, locator_variables, wait_timeout=wait_timeout)
        retry_index += 1
        if ele:
            break
        pass 
    if ele:
        logger.logger.debug('开始点击元素 - {}'.format(str(_locator)))
        cc.find_element(_locator, locator_variables, window_mode).click(mouse_button=mouse_button, by=by, modifier_key=modifier_key, timeout= timeout)
        logger.logger.debug('结束元素点击 - {}'.format(str(_locator)))
        sleep(sleepSeconds)
        return True
    else:
        logger.logger.debug('元素不存在，忽略点击')
        return False
    
def find_elements(
        _locator,
        locator_variables: dict = {},
        timeout: int = 30
    ) -> List[UiElement]:
    logger.logger.debug('开始获取相似元素 - {}'.format(str(_locator)))
    eles = cc.find_elements(_locator, locator_variables, timeout)
    logger.logger.debug('结束获取相似元素 - 匹配{}个结果'.format(len(eles)))
    return eles

def set_text(
        _locator,
        locator_variables: dict = {},
        text: str = '',        
        by: Union[Literal["default", "set-text", "sendkey-after-click", "sendkey-after-focus"], InputTextBy]= InputTextBy.Default,
        overwrite: bool = True,
        timeout: int = 30,
        sleepSeconds: int = 2
    ) -> None:
    logger.logger.debug('开始设置文本 - {} - {}'.format(str(_locator), text))
    try:
        cc.find_element(_locator, locator_variables).set_text(text, by, overwrite, timeout)
        logger.logger.debug('结束设置文本 - {}'.format(str(_locator)))
        sleep(sleepSeconds)
        pass
    except Exception as ex:
        raise RpaException('设置文本{}失败，{}'.format(str(_locator), str(ex)))

def is_existing(
        _locator,
        locator_variables: dict = {},
        timeout: int = 30
    ) -> bool:
    logger.logger.debug('开始检查元素是否存在 - {}'.format(str(_locator)))
    result = cc.is_existing(_locator, locator_variables, timeout)
    logger.logger.debug('结束检查元素是否存在 - {}, 是否存在：{}'.format(str(_locator), result))
    return result

def highlight(
        _locator = Union[_Locator, UiElement],
        locator_variables: dict = {},
        color: Union[str, Color] = Color.Yellow,
        duration: int = 3,        
        timeout: int = 30
    ) -> None: 
    name = str(_locator)
    if isinstance(_locator, UiElement):
        name = 'obj'
    try:
        logger.logger.debug('开始高亮元素 - {}'.format(name))
        if isinstance(_locator, _Locator):
            cc.find_element(_locator, locator_variables).highlight(color, duration, timeout)
            pass
        else:
            _locator.highlight(color, duration, timeout)
        logger.logger.debug('结束高亮元素 - {}'.format(name))
        pass
    except Exception as ex:
        logger.logger.warn('高亮元素失败：{}'.format(str(ex)))
        raise RpaException('高亮元素失败 - {}'.format(name))
    
def hover(
        _locator = Union[_Locator, UiElement],
        locator_variables: dict = {},
        timeout: int = 30
    ) -> None: 
    name = str(_locator)
    if isinstance(_locator, UiElement):
        name = 'obj'
    try:
        logger.logger.debug('开始悬停元素 - {}'.format(name))
        if isinstance(_locator, _Locator):
            cc.find_element(_locator, locator_variables).hover(timeout)
            pass
        else:
            _locator.hover(timeout)
        logger.logger.debug('结束悬停元素 - {}'.format(name))
        pass
    except Exception as ex:
        logger.logger.warn('悬停元素失败：{}'.format(str(ex)))
        raise RpaException('悬停元素失败 - {}'.format(name))
    
def get_text(
        _locator = Union[_Locator, UiElement],
        locator_variables: dict = {},
        timeout: int = 30
    ) -> str: 
    name = str(_locator)
    if isinstance(_locator, UiElement):
        name = 'obj'
    try:
        txt = None
        logger.logger.debug('开始获取文本 - {}'.format(name))
        if isinstance(_locator, _Locator):
            txt = cc.find_element(_locator, locator_variables).get_text(timeout)
        else:
            txt = _locator.get_text(timeout)
        logger.logger.debug('文本内容：' + txt)
        logger.logger.debug('结束获取文本 - {}'.format(name))
        return txt
    except Exception as ex:
        logger.logger.warn('获取文本失败：{}'.format(str(ex)))
        raise RpaException('获取文本失败 - {}'.format(name))


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

def __main__():
    pass