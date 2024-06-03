import asyncio
import multiprocessing
import parser

async def async_fetch_and_parse(url, data_type):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, parser.fetch_and_parse, url, data_type)
    return result

async def run_task(url, data_types):
    tasks = []

    if 'emails' in data_types or 'all' in data_types:
        tasks.append(async_fetch_and_parse(url, ['emails']))
    if 'phone_numbers' in data_types or 'all' in data_types:
        tasks.append(async_fetch_and_parse(url, ['phone_numbers']))
    if 'images' in data_types or 'all' in data_types:
        tasks.append(async_fetch_and_parse(url, ['images']))
    if 'videos' in data_types or 'all' in data_types:
        tasks.append(async_fetch_and_parse(url, ['videos']))
    if 'nips' in data_types or 'all' in data_types:
        tasks.append(async_fetch_and_parse(url, ['nips']))
    results = await asyncio.gather(*tasks)
    final_result = {'url': url}
    for result in results:
        final_result.update(result)
    
    return final_result

def worker(url, data_types, queue, subpages):
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(run_task(url, data_types))
    queue.put(results)
    for subpage in subpages:
        results = loop.run_until_complete(run_task(subpage, data_types))
        queue.put(results)

def run_multiprocessing_task(url, data_types):
    cpu_count = multiprocessing.cpu_count()
    num_subpages = cpu_count * 2
    subpages = parser.fetch_subpages(url, num_subpages)

    manager = multiprocessing.Manager()
    queue = manager.Queue()
    processes = []

    for i in range(cpu_count):
        start = i * 2
        end = start + 2
        p = multiprocessing.Process(target=worker, args=(url, data_types, queue, subpages[start:end]))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    result = {}
    while not queue.empty():
        sub_result = queue.get()
        if 'url' not in result:
            result['url'] = sub_result['url']
        for key in sub_result:
            if key != 'url':
                if key not in result:
                    result[key] = sub_result[key]
                else:
                    result[key].extend(sub_result[key])

    return result