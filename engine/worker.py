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
    
    results = await asyncio.gather(*tasks)
    final_result = {'url': url}
    for result in results:
        final_result.update(result)
    
    return final_result

def worker(url, data_types, queue):
    result = asyncio.run(run_task(url, data_types))
    queue.put(result)

def run_multiprocessing_task(url, data_types):
    cpu_count = multiprocessing.cpu_count()
    manager = multiprocessing.Manager()
    queue = manager.Queue()
    processes = []

    for _ in range(cpu_count):
        p = multiprocessing.Process(target=worker, args=(url, data_types, queue))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    result = {}
    while not queue.empty():
        result.update(queue.get())

    return result
