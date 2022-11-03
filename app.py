import utils
import json
import time


def run_with_retry(func, attempts=10):
    counter = 0
    success = False

    while counter < attempts+1 and not success:
        try:
            func
            success = True
            break
        except Exception as e:
            print(e)
            print('An error occured, retrying...')
            time.sleep(5)
        counter += 1
        if counter == attempts+1:
            print('Max retries exceeded.')
    
    return success


def classify_urls(main_url, url):
    resource_urls = []
    page_urls = []
    result = {}
    
    try:
        network_info = utils.get_network_log(url)
    except Exception as e:
        print(e)
        print('Browser Connection Failed')
        return

    reqs = network_info['request']
    for req in reqs:
        if main_url in req['targetUrl']:
            resource_urls.append(req['targetUrl'])

    try:
        raw_links = utils.get_hyperlinks(url)
    except Exception as e:
        print(e)
        print('Browser Connection Failed')
        return

    valid_url = utils.filter_by_same_domain(raw_links, main_url)

    for item in valid_url:
        if '.html' in item:
            page_urls.append(item)
        else:
            resource_urls.append(item)
    
    result['pages'] = list(set(page_urls))
    result['resources'] = list(set(resource_urls))
    print(json.dumps(result, indent=2))

    return result


def main(main_url, save_path):
    failed_urls = []

    url = 'https://web.stanford.edu/class/cs101/lecture01.html'
    classified_urls = classify_urls(main_url, url)

    for resource in classified_urls['resources']:
        retrieve_status = run_with_retry(utils.download_from_url(resource,main_url, save_path))
        if not retrieve_status:
            failed_urls.append(resource)
    if failed_urls:
        print(failed_urls)
        

main_url = 'https://web.stanford.edu/class/cs101/'
save_path = '/Users/andy13/learning/test'
main(main_url, save_path)

# try:
#     data = utils.get_hyperlinks(url, save_as_json=True)
# except Exception as e:
#     print(e)
#     print('Connection Error')

# try:
#     data = utils.get_network_log(url, save_as_json=True)
# except Exception as e:
#     print(e)
#     print('Connection Error')

# utils.download_from_url('https://web.stanford.edu/class/cs101/', '/Users/andy13/learning/test')