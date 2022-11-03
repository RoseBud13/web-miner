"""浏览器和网络请求工具包

Author: Rosebud
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
import json
import requests
import os


def url_to_filename(url, prefix):
    if 'https' in url:
        filename = prefix + '_' + url[8:].replace('.', '-').replace('/', '_')
    elif 'http' in url:
        filename = prefix + '_' + url[7:].replace('.', '-').replace('/', '_')
    else:
        filename = prefix + '_' + url.replace('.', '-').replace('/', '_')
    return filename


def filter_by_same_domain(url_lists, domain_url):
    links_of_same_domain = []
    for link in url_lists:
        if link and domain_url in link:
            links_of_same_domain.append(link)
    return links_of_same_domain


def get_network_log(url, save_as_json=False, timeout=60):
    """driver.get_log抓取Network数据包
        https://juejin.cn/post/7123039097706250253
        https://www.phpfv.com/view/27.html
    """
    service = ChromeService(executable_path=ChromeDriverManager().install())

    options = webdriver.ChromeOptions()
    # specify perfLoggingPrefs
    options.add_experimental_option('perfLoggingPrefs', {'enableNetwork': True})

    caps = DesiredCapabilities.CHROME.copy()
    # enabled chrome performance logging
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}

    driver = webdriver.Chrome(
        options=options, 
        service=service,
        desired_capabilities=caps
    )
    print('session started')

    # establish waiting strategy
    driver.set_page_load_timeout(timeout)

    print('navigating...')
    driver.get(url)
    print('navigated to {}'.format(url))

    logs = driver.get_log('performance')
    print('performance log loaded')

    req_list = []
    res_list = []

    for log in logs:
        msg = json.loads(log['message'])['message']
        if msg['method'] == 'Network.responseReceived':
            response = msg['params']['response']
            try:
                ip = response['remoteIPAddress']
            except BaseException as e:
                print(e)
                ip = ''
            try:
                port = response['remotePort']
            except BaseException as e:
                print(e)
                port = ''
            res_list.append(
                {
                    'originUrl': response['url'],
                    'remoteIp': ip,
                    'remotePort': port,
                    'httpStatus': response['status'],
                    'httpStatusText': response['statusText'],
                    'mimeType': response['mimeType'],
                    'resourceType': msg['params']['type']
                }
            )
        elif msg['method'] == 'Network.requestWillBeSent':
            req_list.append(
                {
                    'targetUrl': msg['params']['request']['url'],
                    'initiatorType': msg['params']['initiator']['type'],
                    'httpMethod': msg['params']['request']['method'],
                    'resourceType': msg['params']['type']
                }
            )
        else:
            pass

    driver.quit()
    print('session ended')

    result = {
        'response': res_list,
        'request': req_list
    }

    if save_as_json:
        filename = url_to_filename(url, 'network_data')
        with open('data/{}.json'.format(filename), 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
            print('{} json file saved'.format(filename))
    
    return result


def get_hyperlinks(url, save_as_json=False, timeout=60):
    driver = webdriver.Chrome(service=ChromeService(executable_path=ChromeDriverManager().install()))
    print('session started')

    # establish waiting strategy
    driver.set_page_load_timeout(timeout)

    print('navigating...')
    driver.get(url)
    print('navigated to {}'.format(url))

    links = driver.find_elements(By.TAG_NAME, 'a')

    href_lists = []

    for link in links:
        href_lists.append(link.get_attribute('href'))
    
    if save_as_json:
        href_dict = {
            'page_url': url,
            'links': href_lists
        }
        filename = url_to_filename(url, 'links')
        with open('data/{}.json'.format(filename), 'w', encoding='utf-8') as f:
            json.dump(href_dict, f, ensure_ascii=False, indent=4)
            print('{} json file saved'.format(filename))
    
    return href_lists


def download_from_url(url, main_url, path):
    if url[-1:] == '/' or '.' not in url.split('/')[-1]:
        filename = 'index.html'
    else:
        filename = url.split('/')[-1]

    if '/' in url.replace(main_url, ''):
        pre_path = path + '/' + url.replace(main_url, '')
        filepath = pre_path + filename
        isExist = os.path.exists(pre_path )
        if not isExist:
            os.makedirs(pre_path )
    else:
        filepath = path + '/' + filename

    try:
        res = requests.get(url, stream=True)
    except:
        print('Connectiong Error Occured')

    if res.status_code == 200:
        with open(filepath, 'wb') as handler:
            handler.write(res.content)
            print('{} downloaded from {}'.format(filename, url))
    
    else:
        print('{} couldn\'t be retrieved'.format(url))
