"""
This module implements map-reduce approach over the CPU cores. Under the hood
'multiprocessing' module is used to achive the parallel execution.
"""

import multiprocessing as mp
from operator import itemgetter
from queue import Empty
from operator import itemgetter


THREADS_NUM_DEFAULT = mp.cpu_count() // 2


def map_multi(lst, map_func, threads_num=THREADS_NUM_DEFAULT, verbose=False):
    """
    Implements multithread map-function. It returns a list as the result.
    """
    def target(lst, input_queue, result_queue):
        while True:
            try:
                idx = input_queue.get(block=False)
            except Empty:
                break
            else:
                if verbose:
                    print(f"Map for index {idx}")
                elem = lst[idx]
                result = map_func(elem)
                result_queue.put((idx, result))

    input_queue = mp.Queue()
    for idx in range(len(lst)):
        input_queue.put(idx)

    result_queue = mp.Queue()

    processes = [
        mp.Process(target=target, args=(lst, input_queue, result_queue))
        for _ in range(threads_num)
    ]
    list(map(mp.Process.start, processes))

    result_list = []
    while len(result_list) < len(lst):
        idx, elem = result_queue.get(block=True)
        result_list.append((idx, elem))
        if verbose:
            print(f"Map done {len(result_list)} of {len(lst)}")

    result_list.sort(key=itemgetter(0))

    return list(map(itemgetter(1), result_list))


def reduce_multi(lst, reduce_func, threads_num=THREADS_NUM_DEFAULT,
                 verbose=False):
    """
    Implements multithread reduce-function.
    """
    while len(lst) > 1:
        if verbose:
            print(f"Reduce for {len(lst)} items")
        lst_pairs = [
            (lst[i], lst[i + 1])
            for i in range(0, len(lst) - 1, 2)
        ]
        lst_new = map_multi(
            lst_pairs,
            map_func=lambda pair: reduce_func(*pair),
            threads_num=threads_num
        )
        if len(lst) % 2 == 1:
            lst_new.append(lst[-1])
        lst = lst_new
    return lst[0]


def mapreduce_multi(lst, map_func, reduce_func,
                    threads_num=THREADS_NUM_DEFAULT, verbose=False):
    """
    Implements multithreading map-reduce approach over the given list
    with the functions map_func and reduce_func.
    """
    if verbose:
        print("Map stage...")
    lst = map_multi(lst, map_func=map_func, threads_num=threads_num,
                    verbose=verbose)

    if verbose:
        print("Reduce stage...")
    result = reduce_multi(lst, reduce_func=reduce_func,
                          threads_num=threads_num, verbose=verbose)

    if verbose:
        print("Map-reduce completed")
    return result
