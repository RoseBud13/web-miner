import utils
import json

url = 'https://web.stanford.edu/class/cs101/'

try:
    data = utils.get_hyperlinks(url, save_as_json=True)
except Exception as e:
    print(e)
    print('Connection Error')

try:
    data = utils.get_network_log(url, save_as_json=True)
except Exception as e:
    print(e)
    print('Connection Error')