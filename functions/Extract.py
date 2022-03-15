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
def start_threads(elements: dict):
    futures = []
    lock = RLock()

    with ThreadPoolExecutor(max_workers=500) as executor:
        if len(elements) > 100:
            disable_tqdm = False
            prt = noprint
        else:
            disable_tqdm = True
            prt = toprint

        print('\nLoading the threads... :')
        for file_path, dest_path in tqdm(elements.items(), disable=disable_tqdm):
            th = executor.submit(move, lock, file_path, dest_path, prt)
            futures.append(th)

        if not disable_tqdm:
            print('\nWaiting for threads to finish... :')

        for th in tqdm(as_completed(futures), disable=disable_tqdm):
            th.result()

        print("Done!")


def find_dest_paths(file_paths: List[str], main_dest: str):
    """
    Find the destination of each file.
    """

    # dictionary containing the pair {file_path: dest_path} for each file
    dict_src_dest = dict()

    for file_path in file_paths:
        # Find the name of the file and add it to the destination
        filename = os.path.basename(file_path)
        dest = os.path.join(main_dest, filename)

        dict_src_dest[file_path] = dest

    return dict_src_dest


def extract_all(main_path, main_dest):
    start = time.time()

    print(f'Main folder: {main_path}\n')

    print('\nSearching all the files... it may take a while...\n')
    file_paths: list = find_files(main_path, skip_files_in_main_folder=True)
    print('Done!')

    print('\nLooking where to move the files...')
    dict_src_dest: dict = find_dest_paths(file_paths,  main_dest)
    print('Done!')

    print('\nChecking already existing files...')
    dict_src_dest: dict = find_dest_path_without_conflicts(dict_src_dest)
    print('Done!')

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
