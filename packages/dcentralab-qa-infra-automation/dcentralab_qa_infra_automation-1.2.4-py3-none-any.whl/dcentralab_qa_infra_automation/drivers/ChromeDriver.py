from dcentralab_qa_infra_automation.drivers.HelperFunctions import addExtensionToChrome
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import pytest

from dcentralab_qa_infra_automation.drivers.HelperFunctions import get_chrome_driver_version

"""
init chrome driver, using ChromeDriverManager for chromeDriver installation

@Author: Efrat Cohen
@Date: 11.2022
"""


def initChromeDriver():
    """
    init chrome driver, using ChromeDriverManager for chromeDriver installation
    :return: driver - driver instance
    """
    pytest.logger.info("chrome driver type injected, initialize chrome browser")
    if pytest.data_driven.get("OS") == "windows":
        chrome_service = Service(executable_path=ChromeDriverManager(get_chrome_driver_version()).install())
    else:
        chrome_service = Service(executable_path=ChromeDriverManager(get_chrome_driver_version()).install())
    driver = webdriver.Chrome(service=chrome_service)
    return driver


def initChromeDriverWithExtension():
    """
    init chrome driver with CRX extension, using ChromeDriverManager for chromeDriver installation
    :return: driver - driver instance
    """
    options = webdriver.ChromeOptions()
    options.add_extension(addExtensionToChrome())
    if pytest.data_driven.get("OS") == "windows":
        chrome_service = Service(executable_path=ChromeDriverManager(get_chrome_driver_version()).install())
    else:
        chrome_service = Service(
            executable_path=ChromeDriverManager(get_chrome_driver_version()).install())
    driver = webdriver.Chrome(service=chrome_service, options=options)
    return driver

def initChromeDriverWithExtension(self):
    """
    init chrome driver with CRX extension, using ChromeDriverManager for chromeDriver installation
    :return: driver - driver instance
    """
    chrome_path = r"C:\Users\Efrat Cohen\Downloads\chromedriver-win32\chromedriver-win32\chromedriver.exe"  # Replace with the actual path
    options = webdriver.ChromeOptions()
    options.add_extension(addExtensionToChrome())
    driver = webdriver.Chrome(executable_path=chrome_path, options=options)
    self.driver = driver
    pytest.driver = driver
    return driver
