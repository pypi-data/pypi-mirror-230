# Hi @Edgar, could you please help to do some research for this?
import pytest
from unittest.mock import Mock
from liveramp_automation.utils.selenium import SeleniumUtils


@pytest.fixture
def mock_chrome_driver():
    mock_driver = Mock()
    mock_driver.current_url = 'https://liveramp.com/careers/'
    mock_driver.title = 'Liveramp'
    return mock_driver


def test_open_page(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    my_selenium_instance.get_url(mock_chrome_driver.url)
    ##
    # mock_chrome_driver.url.assert_called_once()


def test_navigate_to_url(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    my_selenium_instance.navigate_to_url(path='/test', query='param=value')


def test_refresh_page_url(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    my_selenium_instance.refresh_page()
    bbb = my_selenium_instance.get_page_url()
    assert bbb == mock_chrome_driver.current_url


def test_get_title(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    result = my_selenium_instance.get_title()
    assert result == "Liveramp"


def test_save_screenshot(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    my_selenium_instance.save_screenshot('test_screenshot')
