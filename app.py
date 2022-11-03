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


resource_urls = []
result = {}
recursing_counter = 0


def get_all_resources(main_url, url):
    global recursing_counter
    recursing_counter += 1
    print('################# 第 {} 次循环 #################'.format(recursing_counter))

    page_urls = []

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
        if '.html' in item and item != url:
            page_urls.append(item)
        else:
            resource_urls.append(item)

    if page_urls:
        for page in page_urls:
            return get_all_resources(main_url, page)
    else:
        # result['pages'] = page_urls
        result['resources'] = resource_urls
        print(json.dumps(result, indent=2))
        return result


def main(main_url, save_path):
    failed_urls = []
    url = main_url

    classified_urls = get_all_resources(main_url, url)

    if classified_urls and classified_urls['resources']:
        for resource in classified_urls['resources']:
            retrieve_status = run_with_retry(utils.download_from_url(resource,main_url, save_path))
            if not retrieve_status:
                failed_urls.append(resource)
        if failed_urls:
            print(failed_urls)
    else:
        print('No resource found on {}'.format(main_url))


main_url = 'https://web.stanford.edu/class/cs101/'
save_path = '/Users/andy13/learning/test'
main(main_url, save_path)
