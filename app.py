import utils
import json
import time


def run_with_retry(func, *func_args, retry_count=5, delay=5):
    for _ in range(retry_count):  # all tries happen in the loop
        if func(*func_args):
            return True           # if we succeed we return True
        print('An error occured')
        print("Waiting for {} seconds before retyring again...".format(delay))
        time.sleep(delay)
    print('Max retries exceeded.')
    return False


page_urls = []
resource_urls = []
result = {}
recursing_counter = 0
checked_page = set()


def get_all_resources(main_url, url):
    global page_urls
    global resource_urls
    global recursing_counter
    global checked_page

    recursing_counter += 1
    print('################# 第 {} 次循环 #################'.format(recursing_counter))

    temp_page_urls = []
    checked_page.add(url)
    print(checked_page)

    if recursing_counter > 1:
        page_urls.pop(0)
    
    # for page in checked_page:
    #     if page in page_urls:
    #         page_urls.remove(page)

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
        if item not in checked_page:
            if '.html' in item and item != url:
                temp_page_urls.append(item)
            else:
                resource_urls.append(item)

    print('temp', temp_page_urls)
    page_urls = page_urls + temp_page_urls
    print('page_urls', page_urls)
    # print('resources', json.dumps(resource_urls, indent=2))

    for page in page_urls:
        print(page)
        if page in checked_page:
            # page_urls.remove(page)
            continue
        return get_all_resources(main_url, page)
   
    result['resources'] = list(set(resource_urls))
    print(json.dumps(result, indent=2))
    return result


def main(main_url, save_path):
    failed_urls = []
    url = main_url

    classified_urls = get_all_resources(main_url, url)

    if classified_urls and classified_urls['resources']:
        for resource in classified_urls['resources']:
            retrieve_status = run_with_retry(utils.download_from_url, resource, main_url, save_path)
            if not retrieve_status:
                failed_urls.append(resource)
        if failed_urls:
            print(failed_urls)
    else:
        print('No resource found on {}'.format(main_url))


main_url = 'https://web.stanford.edu/class/cs101/'
save_path = '/Users/andy13/learning/test'
main(main_url, save_path)


# def run_with_retry(func, attempts=5):
#     counter = 0
#     success = False

#     while counter < attempts+1 and not success:
#         try:
#             func
#             success = True
#             break
#         except Exception as e:
#             print(e)
#             print('An error occured, retrying...')
#             time.sleep(5)
#         counter += 1
#         if counter == attempts+1:
#             print('Max retries exceeded.')
    
#     return success


# def test(main_url, save_path):
#     failed_urls = []
#     with open('data/test.json', 'r') as f:
#         rsrc = json.load(f)
#     for r in rsrc:
#         retrieve_status = run_with_retry(utils.download_from_url, r, main_url, save_path)
#         if not retrieve_status:
#             failed_urls.append(r)
#     if failed_urls:
#         print(failed_urls)
 

#test(main_url, save_path)
