__version__ = "1.0.1"

from datetime import datetime, timedelta
import os
from clicknium import clicknium as cc, locator, ui
from time import sleep
import clr
from botnium.common.models import TypeMothod

from botnium.common.utils import Utils

source_path = Utils.get_libfolder()
dlls = Utils.get_import_dlls(source_path)
for dll in dlls:
    dll_path = os.path.join(source_path, dll)
    clr.AddReference(dll_path)
# clr.AddReference(os.path.join(os.getcwd(), "lib", "CSharpRPA.dll"))
from CSharpRPA.FileHelpers import *
from CSharpRPA.RegisterHelpers import *
from CSharpRPA.UI import *
from CSharpRPA.Notifications import *
# clr.AddReference(os.path.join(os.getcwd(), "lib", "KeyboardCollection.dll"))
import KeyboardCollection as kb

def del_files(filepath, target_suffix):
    files = os.listdir(filepath)
    for file in files:
        if '.' in file:
            suffix = file.split('.')[-1]
            if suffix == target_suffix:
                os.remove(os.path.join(filepath, file))

def get_files(filepath, target_suffix):
    match_files = []
    files = os.listdir(filepath)
    for file in files:
        if '.' in file:
            suffix = file.split('.')[-1]
            if suffix == target_suffix:
                match_files.append(os.path.join(filepath, file))
    return match_files

def remove_file_if_exists(filepath):
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        finally:
            # 忽略异常
            pass

def parse_month(month):
        if month == 1:
            return '一月'
        if month == 2:
            return '二月'
        if month == 3:
            return '三月'
        if month == 4:
            return '四月'
        if month == 5:
            return '五月'
        if month == 6:
            return '六月'
        if month == 7:
            return '七月'
        if month == 8:
            return '八月'
        if month == 9:
            return '九月'
        if month == 10:
            return '十月'
        if month == 11:
            return '十一月'
        if month == 12:
            return '十二月'
        pass


'''
Function Keys: [enter],[esc],[alt],[tab],[backspace],[clear],[shift],[capelock],[ctrl]
'''
def input_function(func):
    keyop = kb.Wingring0Keyboard()  
    keyop.Input(func)
    sleep(0.3)
    
def clear_text(times, type: TypeMothod = TypeMothod.Ring):
    if type == TypeMothod.Ring:
        keyop = kb.Wingring0Keyboard()  
        for i in range(0, times):
            keyop.Input("[backspace]")
            sleep(0.3)
    else:
        keyop = kb.AutoKeyboard()
        sleep(2)
        for i in range(0, times):
            keyop.InputFunctionKey("{BACKSPACE}")
            sleep(0.3)

def input_text(text, type: TypeMothod = TypeMothod.Ring):
    if type == TypeMothod.Ring:
        keyop = kb.Wingring0Keyboard()
        for c in text:
            keyop.Input(c)
            sleep(0.6)
    else:
        keyop = kb.AutoKeyboard()
        sleep(2)
        keyop.Input(text, 300)


'''监听下载文件路径'''
def monitorFileDownload(folder, lastDateTime, extensions):
    monitor = FileMonitor(folder, lastDateTime, extensions, 60)
    file_path = monitor.GetDownloadFilePath()
    # sleep(10) # 某些文件下载会扫描
    return file_path

'''删除指定路径下匹配的文件'''
def remove_files(folder, searchPattern):
    DirectoryHelper.RemoveFiles(folder, searchPattern)

'''dlt格式转csv（如：工商银行流水文件）'''
def dlt2Csv(file, startIndex):
    csvPath = DltFileHelper.ToCsv(file, startIndex)
    return csvPath

'''
配置选项及对应10进制几个组合为：
SSL2.0   00000008(8)
SSL3.0   00000020(32)
TLS1.0 00000080(128)
TLS1.1 00000200(512)
TLS1.2 00000800(2048)

TLS1.3 00002000(8192)
TLS1.1 TLS1.2   00000a00(2560)
SSL3.0 TLS1.0   000000a0(160)  //32+128=160
SSL3.0 TLS1.0 TLS1.1   000002a0(672)      
SSL3.0 TLS1.0 TLS1.2   000008a0(2208)
SSL3.0 TLS1.0 TLS1.1 TLS1.2   00000aa0(2720)
SSL2.0 SSL3.0 TLS1.0 TLS1.1 TLS1.2 00000aa8(2728)
链接：https://blog.csdn.net/dong123ohyes/article/details/127983040
'''
def setSecureProtocols(v):
    IESettings.SetSecureProtocols(v)

def enableTLS1_2():
    setSecureProtocols(2720)
    pass

def disableTLS1_2():
    setSecureProtocols(672)
    pass

def setDefaultProtocols():
    setSecureProtocols(160)
    pass

def toast(message, title = '', duration = 2):
    ToastHelper.Show(title, message, duration)
    pass

def send_wx_message(message, title = '', url = ''):
    webhookConfig = WebHookItem()
    webhookConfig.Platform = WebHookType.WXWork
    webhookConfig.Url = url
    webhookService = WebhookService(webhookConfig)
    webhookService.SendMarkdown(message, title)
    pass
def send_wx_file(file_path, url = ''):
    webhookConfig = WebHookItem()
    webhookConfig.Platform = WebHookType.WXWork
    webhookConfig.Url = url
    webhookService = WebhookService(webhookConfig)
    webhookService.SendFile(file_path)
    pass