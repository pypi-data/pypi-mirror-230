import pytest
from unittest.mock import Mock
from liveramp_automation.utils.playwright import PlaywrightUtils


@pytest.fixture
def mock_playwright_page():
    mock_page = Mock()
    mock_page.url = 'https://liveramp.com/careers/'
    mock_page.title = 'Liveramp'
    return mock_page


def test_save_screenshot(mock_playwright_page):
    my_page_instance = PlaywrightUtils(mock_playwright_page)
    my_page_instance.save_screenshot('test_screenshot')
    assert mock_playwright_page.screenshot.called


def test_navigate_to_url(mock_playwright_page):
    my_page_instance = PlaywrightUtils(mock_playwright_page)
    my_page_instance.navigate_to_url(path='/test', query='param=value')
    assert mock_playwright_page.goto.called
    # mock_playwright_page.goto('https://liveramp.com/test?param=value').assert_called_once()


def test_close_page_banner(mock_playwright_page):
    my_page_instance = PlaywrightUtils(mock_playwright_page)
    my_page_instance.close_popup_banner()

#
# import pytest
# from unittest.mock import patch
# from liveramp_automation.utils.playwright import PlaywrightUtils
#
#
# @patch('liveramp_automation.utils.playwright.PlaywrightUtils')
# def test_save_screenshot(mock_playwright_page):
#     mock_page_instance = mock_playwright_page.return_value
#     mock_page_instance.url = 'https://liveramp.com/careers/'
#     mock_page_instance.title = 'Liveramp'
#
#     my_page_instance = PlaywrightUtils(mock_page_instance)
#     my_page_instance.save_screenshot('test_screenshot')
#     assert mock_page_instance.screenshot.called
#     # mock_page_instance.save_screenshot.assert_called_with(path='test_screenshot')
#
#
# @patch('liveramp_automation.utils.playwright.PlaywrightUtils')
# def test_navigate_to_url(mock_playwright_page):
#     mock_page_instance = mock_playwright_page.return_value
#     mock_page_instance.url = 'https://liveramp.com/careers/'
#     mock_page_instance.title = 'Liveramp'
#
#     my_page_instance = PlaywrightUtils(mock_page_instance)
#     my_page_instance.navigate_to_url(path='/test', query='param=value')
#     assert mock_page_instance.goto.called
#
#     # mock_page_instance.goto('https://liveramp.com/test?param=value').assert_called_once()
