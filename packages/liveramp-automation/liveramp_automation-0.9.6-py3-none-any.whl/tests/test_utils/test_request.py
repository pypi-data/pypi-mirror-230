from liveramp_automation.utils.request import request_post, request_get


def test_request_post():
    url = 'https://run.mocky.io/v3/0d9a5896-aeaa-4df1-8368-8917c457f52b'
    headers = None
    response = request_post(url, headers, data=None)
    assert response
    assert response.ok


def test_request_get():
    url = 'https://www.google.com/'
    headers = None
    response = request_get(url, headers)
    assert response
    assert response.ok
