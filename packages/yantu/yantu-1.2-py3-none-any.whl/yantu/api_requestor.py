import requests

BASE_URL = 'http://localhost:8555/api/v1/'


# BASE_URL = 'http://www.yantu-tech.com/api/v1'

def _make_request(endpoint, data):
    """
    执行请求
    :param endpoint:
    :param data:
    :return:
    """
    url = BASE_URL + endpoint
    response = requests.post(url, json=data)
    response.raise_for_status()
    return response
