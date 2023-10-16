"""
WebDriverWrapper 类说明文档
作者：Lin Wang

概述：
WebDriverWrapper 类是一个对 Selenium WebDriver (特别是 Chrome 类) 的扩展，用于在执行 Web UI 测试时自动记录 webdriver 操作。
当调用常用的方法，如 get、find_element、click 等时，这些操作将自动记录到 logger 中。

使用说明：
1. 导入 WebDriverWrapper 类：
   从 webdriver_wrapper 模块导入 WebDriverWrapper 类。

2. 创建 WebDriverWrapper 实例：
   在测试框架中，使用 WebDriverWrapper 类替换原来的 Chrome webdriver 实例。将 logger 对象和其他所需参数传入 WebDriverWrapper 的构造函数中。

示例代码：

from selenium.webdriver import ChromeOptions
from webdriver_wrapper import WebDriverWrapper

class MyTestCase:
    def __init__(self, logger):
        self.logger = logger
        chrome_options = ChromeOptions()
        # 使用 WebDriverWrapper 替换原来的 webdriver 实例
        self.browser = WebDriverWrapper(self.logger, options=chrome_options)

    def run_test(self):
        self.browser.get("https://www.bing.com")
        # 其他测试代码

功能说明：
1. _log_action 方法：
   用于记录操作到 logger。在为其他 webdriver 方法添加日志记录功能时，可以调用此方法。

2. 常用方法的日志记录功能：
   WebDriverWrapper 类已经为以下方法添加了日志记录功能：
   - get
   - find_element
   - find_elements
   - click
   - send_keys
   - clear
   - execute_script

   根据需要，您可以继续为其他 webdriver 方法添加日志记录功能，只需在 WebDriverWrapper 类中重写这些方法并调用 _log_action() 即可。
"""

from selenium.webdriver import Chrome


from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By

class WebDriverWrapper(Chrome):
    def __init__(self, logger, *args, **kwargs):
        self.logger = logger
        super().__init__(*args, **kwargs)

    def _log_action(self, action, *args):
        msg = f">>>>>>>>>>>>>>>>>> Action: {action} called with arguments: {', '.join(map(str, args))}"
        self.logger.info(msg)

    def get(self, url):
        self._log_action("get", url)
        super().get(url)

    def find_element(self, by=By.ID, value=None):
        self._log_action("find_element", by, value)
        return super().find_element(by, value)

    def find_elements(self, by=By.ID, value=None):
        self._log_action("find_elements", by, value)
        return super().find_elements(by, value)

    def click(self, element):
        self._log_action("click", element)
        element.click()

    def send_keys(self, element, *value):
        self._log_action("send_keys", element, *value)
        element.send_keys(*value)

    def clear(self, element):
        self._log_action("clear", element)
        element.clear()

    def execute_script(self, script, *args):
        self._log_action("execute_script", script, *args)
        return super().execute_script(script, *args)

    # 根据需要，您可以继续在此处添加其他 WebDriver 方法的日志记录功能