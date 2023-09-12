Python toolkits for RPA projects.
- logging
- utility methods
- cc extensions

Sample
``` python
import botnium as bot
import botnium.logger as logger
from botnium.common import *
from clicknium import clicknium as cc, locator

logger = logger.logger
bot.is_existing(locator.explorer.edit_name)  # 判断是否存在
bot.wait_appear(locator.explorer.edit_name)  # 等待元素出现
bot.try_click(locator.explorer.edit_name, wait_timeout=10)  # 如果元素出现，则点击。否则忽略

logger.debug('Debug test logging')
logger.info('Info test logging')

remove_file_if_exists("")  # 移除文件如果存在
toast('Hello')  # Toast通知

```