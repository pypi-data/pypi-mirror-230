#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2022/3/29 1:43 PM
# @Author  : zhengyu.0985
# @FileName: webdriver_common.py
# @Software: PyCharm

import logging
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from typing import List

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
logger = logging.getLogger("my_driver")


class WebDriverCommon(object):
    driver = None
    action = None

    @classmethod
    def _browser_options(cls, browser_type='Chrome'):
        if browser_type == 'Firefox':
            options = webdriver.FirefoxOptions()
        elif browser_type == 'IE':
            options = webdriver.IeOptions()
        else:
            options = webdriver.ChromeOptions()
        # 像Options中添加实验选项。
        options.add_experimental_option(name="excludeSwitches", value=["enable-automation"])
        options.add_argument("--headless")
        return options

    @classmethod
    def init_driver(cls, driver_type='Chrome', executable_path=None):
        if cls.driver is None:
            if executable_path is None:
                if driver_type == 'Firefox':
                    cls.driver = webdriver.Firefox(options=cls._browser_options(browser_type=driver_type))
                elif driver_type == 'IE':
                    cls.driver = webdriver.Ie(options=cls._browser_options(browser_type=driver_type))
                else:
                    cls.driver = webdriver.Chrome(options=cls._browser_options())
            else:
                service_obj = Service(executable_path=executable_path)
                # Chrome类的初始化，executable_path已不建议使用，所以使用Service对象。
                if driver_type == 'Firefox':
                    cls.driver = webdriver.Firefox(service=service_obj,
                                                   options=cls._browser_options(browser_type=driver_type))
                elif driver_type == 'IE':
                    cls.driver = webdriver.Ie(service=service_obj,
                                              options=cls._browser_options(browser_type=driver_type))
                else:
                    cls.driver = webdriver.Chrome(service=service_obj, options=cls._browser_options())

            logger.info('The driver object of WebDriverCommon class was successfully initialized.')
        else:
            logger.warning('The driver object of WebDriverCommon class has been already initialized.')

    @classmethod
    def navigate(cls, url):
        cls.driver.get(url)

    @classmethod
    def refresh(cls):
        cls.driver.refresh()

    @classmethod
    def max_window(cls):
        cls.driver.maximize_window()

    @classmethod
    def min_window(cls):
        cls.driver.minimize_window()

    @classmethod
    def set_action(cls):
        if cls.driver is None:
            logger.error("Driver is None, so cannot initialize ActionChains.")
        else:
            cls.action = ActionChains(cls.driver)
            logger.info("Initialize ActionChains successfully by Driver.")

    @classmethod
    def is_ele_exist(cls, by_locator: str, locator_value: str) -> bool:
        # e.g: element = driver.find_element(By.ID, 'foo')
        try:
            web_ele = cls.driver.find_element(by_locator, locator_value)
            if web_ele is None:
                logger.warning("[失败]：{}={}, 未能定位到WebElement".format(by_locator, locator_value))
                return False
            else:
                logger.info("[成功]：{}={}, 成功定位到WebElement".format(by_locator, locator_value))
                return True
        except Exception as e:
            logger.warning("[异常]：{}={}, 未能定位到WebElement".format(by_locator, locator_value))
            logger.warning(e.args)
            return False
        finally:
            logger.info("is_ele_exist class func has been executed.")

    @classmethod
    def switch_to_new_window(cls):
        handles_list = cls.driver.window_handles()
        for handle in handles_list:
            if handle == cls.driver.current_window_handle:
                pass
            else:
                cls.driver.switch_to.window(handle)

    @classmethod
    def wait_implicitly(cls, time_in_seconds):
        cls.driver.implicitly_wait(time_to_wait=time_in_seconds)

    @classmethod
    def wait_for_load(cls, tuple_locator: tuple, presence_or_visibility='visibility', time_out=10, frequency=0.5) -> WebElement:
        try:
            web_driver_wait = WebDriverWait(cls.driver, timeout=time_out, poll_frequency=frequency)
            if presence_or_visibility == 'visibility':
                result = web_driver_wait.until(method=EC.visibility_of_element_located(tuple_locator),
                                               message="超时未找到")
            elif presence_or_visibility == 'presence':
                result = web_driver_wait.until(method=EC.presence_of_element_located(tuple_locator),
                                               message="超时未找到")
            else:
                logger.warning("presence_or_visibility only supports visibility or presence.")
                result = None
            if isinstance(result, WebElement):
                logger.info("Locator={}, 元素已成功加载。".format(tuple_locator))
            else:
                logger.warning("未等到元素加载。")
                logger.info("result={}".format(result))
            return result
        except Exception as e:
            logger.error(e.args)
            logger.error(e)
        finally:
            logger.info("wait_for_load method has been executed.")

    @classmethod
    def find_element(cls, by_locator: str, locator_value: str, curr_web_ele=None) -> WebElement:
        try:
            if curr_web_ele is None:
                web_ele = cls.driver.find_element(by_locator, locator_value)
                logger.info("[成功]：{}={}, 成功定位到WebElement".format(by_locator, locator_value))
            elif isinstance(curr_web_ele, WebElement):
                web_ele = curr_web_ele.find_element(by_locator, locator_value)
                logger.info("[成功]：基于当前Element[{}], 通过 {}={}, 成功定位到WebElement".format(curr_web_ele, by_locator, locator_value))
            else:
                logger.info("所传参数curr_web_ele类型错误，必须是WebElement类型。")
                web_ele = None
        except Exception as e:
            logger.error(e.args)
            web_ele = None
        finally:
            logger.info("find_element method has been executed.")
        return web_ele

    @classmethod
    def find_element_list(cls, by_locator: str, locator_value: str, curr_web_ele=None) -> List[WebElement]:
        try:
            if curr_web_ele is None:
                web_ele_list = cls.driver.find_elements(by_locator, locator_value)
                logger.info("[成功]：{}={}, 成功获取到WebElement List。".format(by_locator, locator_value))
            elif isinstance(curr_web_ele, WebElement):
                web_ele_list = curr_web_ele.find_elements(by_locator, locator_value)
                logger.info("[成功]：基于当前Element[{}], 通过 {}={}, 成功获取到WebElement List。".format(curr_web_ele, by_locator, locator_value))
            else:
                logger.info("所传参数curr_web_ele类型错误，必须是WebElement类型。")
                web_ele_list = []
        except Exception as e:
            logger.error(e.args)
            web_ele_list = []
        finally:
            logger.info("find_element_list method has been executed.")
        return web_ele_list

    @classmethod
    def switch_to_iframe(cls, frame_id_name_ele):
        # driver.switch_to.frame('frame_name')
        # driver.switch_to.frame(1)
        # driver.switch_to.frame(driver.find_elements(By.TAG_NAME, "iframe")[0])
        try:
            if isinstance(frame_id_name_ele, int):
                cls.driver.switch_to.frame(frame_id_name_ele)
                logger.info("通过Integer Index={}, 进入iFrame。".format(frame_id_name_ele))
            elif isinstance(frame_id_name_ele, str):
                cls.driver.switch_to.frame(frame_id_name_ele)
                logger.info("通过iFrame Name={}, 进入iFrame。".format(frame_id_name_ele))
            elif isinstance(frame_id_name_ele, WebElement):
                cls.driver.switch_to.frame(frame_id_name_ele)
                logger.info("通过iFrame WebElement={}, 进入iFrame。".format(frame_id_name_ele))
            else:
                logger.warning("frame_id_name_ele参数，仅支持int、str、WebElement类型。")
        except Exception as e:
            logger.error(e.args)
        finally:
            logger.info("switch_to_iFrame method has been executed.")

    @classmethod
    def switch_to_default_content(cls):
        cls.driver.switch_to.default_content()

    @classmethod
    def right_click(cls, on_web_ele, int_down_times):
        if cls.action is None:
            logger.error("尚未未初始化ActionChains对象action.")
        else:
            cls.action.context_click(on_element=on_web_ele).perform()
            for i in range(int_down_times):  # 当前点击向下键无反应。
                # cls.action.send_keys(Keys.ARROW_DOWN)
                cls.action.key_down(Keys.ARROW_DOWN)
                cls.wait_implicitly(1)
                cls.action.key_up(Keys.ARROW_DOWN)
                logger.info("第{}次点击向下键。".format(i))
            cls.action.send_keys(Keys.ENTER)
            logger.info("回车选中。")

    @classmethod
    def move_to_ele(cls, web_ele, x_off_set=None, y_off_set=None):
        if web_ele is None:
            logger.error("给定WebElement is None.")
            return None
        elif x_off_set is None or y_off_set is None:
            return cls.action.move_to_element(web_ele)
        else:
            return cls.action.move_to_element_with_offset(web_ele, xoffset=x_off_set, yoffset=y_off_set)

    @classmethod
    def close_driver(cls):
        cls.driver.close()
        logger.info("成功关闭WebDriver")


if __name__ == '__main__':
    WebDriverCommon.init_driver(executable_path='./chromedriver.exe')
    WebDriverCommon.navigate("https://www.baidu.com")
    WebDriverCommon.refresh()
    WebDriverCommon.max_window()
    logger.info(WebDriverCommon.is_ele_exist(By.ID, "s-top-left"))
    ele = WebDriverCommon.wait_for_load((By.XPATH, "//div[@id='s-top-left']/a[1]"))
    logger.info(type(ele))
    logger.info(ele)
    WebDriverCommon.set_action()
    # WebDriverCommon.right_click(ele, 3)  # 该功能有Bug
    WebDriverCommon.wait_implicitly(3)  # 该功能不生效
    search_input = (By.ID, 'kw')
    search_button = (By.ID, 'su')
    WebDriverCommon.find_element(*search_input).send_keys("郑宇")
    WebDriverCommon.find_element(*search_button).click()
    time.sleep(3)
    WebDriverCommon.close_driver()
