import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import RLock
from timebudget import timebudget
from tqdm import tqdm

from basefunctions import *
from Delete import *


# ------------------------------------------------ Extract All -------------------------------------------

@timebudget
def find_dest_path(paths, dest):
    finalPaths = {}

    print('Processing the files...\n')
    for path in tqdm(paths):
        basename, filename = os.path.split(path)

        name, ext = os.path.splitext(filename)
        i, num = findNum(name)

        destPath = os.path.join(dest, filename)

        while os.path.exists(destPath) or destPath in finalPaths:
            num += 1
            destName = name[:i] + '(' + str(num) + ')' + ext
            destPath = os.path.join(dest, destName)

        finalPaths[destPath] = path

    return finalPaths


@timebudget
def start_threads(elements: dict):
    futures = []
    lock = RLock()

    with ThreadPoolExecutor(max_workers=100) as executor:
        if len(elements) > 100:
            disable_tqdm = False
            prt = noprint
        else:
            disable_tqdm = True
            prt = toprint

        print('Loading the threads... :')
        for destPath in tqdm(elements.keys(), disable=disable_tqdm):
            path = elements[destPath]
            th = executor.submit(move, lock, path, destPath, prt)
            futures.append(th)

        if not disable_tqdm:
            print('\nWaiting for threads to finish... :')

        for th in tqdm(as_completed(futures), disable=disable_tqdm):
            th.result()


def extract_all(main_path, main_dest):
    start = time.time()
    print('Searching all the files... it may take a while...\n')

    files_to_move: list = find_files(main_path, main_dest)
    dict_src_dest: dict = find_dest_path(files_to_move, main_dest)
    start_threads(dict_src_dest)

    print(f'\n\nTime Elapsed: {time.time() - start:.5f}')


def extract_all_outside(main_paths, command_vars=''):
    start = time.time()
    print(f"Extracting all files of {main_paths} outside of the folder")

    main_paths: list = clean_paths(main_paths)
    main_path: str = main_paths[0]
    main_dest: str = os.path.dirname(main_path)

    extract_all(main_path, main_dest)

    del_empty_dirs(main_path)

    print(f'\n\nTime Elapsed: {time.time() - start:.5f}')
    input('\n\nPress Enter to continue...')


def extract_all_inside(main_paths, command_vars=''):
    start = time.time()
    print(f"Extracting all files of {main_paths} inside the folder")

    main_paths: list = clean_paths(main_paths)
    main_path: str = main_paths[0]
    main_dest: str = main_path

    extract_all(main_path, main_dest)

    del_empty_dirs(main_path)

    print(f'\n\nTime Elapsed: {time.time() - start:.5f}')
    input('\n\nPress Enter to continue...')


if __name__ == "__main__":
    pass
    print('Done')
