import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import RLock
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm

from basefunctions import *
from Delete import *
from Extract import *

import basefunctions


def find_union_paths(file_paths: List[str], src_folder: str, dest_folder: str):
    """
    Find where each file needs to be moved depending on its extension.
    The folder structure is preserved.
    """

    # dictionary containing the pair {file_path: new_path} for each file
    dict_src_dest = dict()

    for file_path in file_paths:
        # Replace dest in the filename with ext_folder
        new_path = file_path.replace(src_folder, dest_folder)

        dict_src_dest[file_path] = new_path

    return dict_src_dest


def start_threads(dict_src_dest: Dict[Path, Path]):
    futures = list()
    lock = RLock()

    with ThreadPoolExecutor(max_workers=100) as executor:
        if len(dict_src_dest) > 2000:
            dis = False
            prt = basefunctions.noprint
        else:
            dis = True
            prt = basefunctions.toprint

        print('Loading the threads... :')
        for src, dest in tqdm(dict_src_dest.items(), disable=dis):
            Path(dest).mkdir(parents=True, exist_ok=True)
            # make_parent_folders(dest, lock)

            th = executor.submit(move, lock, src, dest, prt)
            futures.append(th)

        if not dis:
            print('\nWaiting for threads to finish... :')

        for th in tqdm(as_completed(futures), disable=dis):
            th.result()


def join(main_paths, command_vars='', disable_input=False):
    start = time.time()

    main_path = Path(main_paths[0])

    print(f'Main folder: {main_path}\n')

    folders_to_join = list()
    for item in os.listdir(main_path):
        if os.path.isdir(os.path.join(main_path, item)):
            folders_to_join.append(item)

    if len(folders_to_join) < 2:
        print('There are not enough folders to join.')
        input('Press Enter to exit...')
        sys.exit()

    print(f'The following folders will be joined inside {folders_to_join[0]}')
    for sub_folder in folders_to_join:
        print(f' - {sub_folder}')

    # ask confirmation to proceed
    while True:
        ans = input('Do you want to proceed? [y/n]')
        if ans.lower() == 'y':
            break
        elif ans.lower() == 'n':
            sys.exit()
        else:
            print('Wrong answer.')

    main_dest = os.path.join(main_path, folders_to_join[0])
    dict_src_dest = dict()
    print('\nSearching all the files to move, it may take a while...')
    for sub_folder in folders_to_join[1:]:
        sub_folder_path = os.path.join(main_path, sub_folder)
        file_paths: List[str] = find_files(sub_folder_path)

        # Add the new srcs and dests to the dictionary
        dict_src_dest = dict_src_dest | find_union_paths(file_paths, sub_folder_path, main_dest)

    print('Done!')

    start_threads(dict_src_dest)

    del_empty_dirs(main_path)

    print(f'\n\nTime Elapsed: {time.time() - start:.5f}')
    if not disable_input:
        input('\n\nPress Enter to continue...')


# todo: it doesn't work because the program is executed on each folder, not one time on all of them
def join_selected(main_paths, command_vars='', disable_input=False):
    start = time.time()

    main_paths = [Path(folder) for folder in main_paths]

    if len(main_paths) < 2:
        input('You need to select at least two folders...\n'
              'Press enter to exit...')
        sys.exit()

    folders_to_join = main_paths
    main_path = main_paths[0]

    print(f'Main folder: {main_path}\n')

    print(f'The following folders will be joined inside {main_path}')
    for sub_folder in folders_to_join:
        print(f' - {sub_folder}')

    # ask confirmation to proceed
    while True:
        ans = input('Do you want to proceed? [y/n]')
        if ans.lower() == 'y':
            break
        elif ans.lower() == 'n':
            sys.exit()
        else:
            print('Wrong answer.')

    main_dest = os.path.join(main_path, folders_to_join[0])
    dict_src_dest = dict()
    print('\nSearching all the files to move, it may take a while...')
    for sub_folder in folders_to_join[1:]:
        sub_folder_path = os.path.join(main_path, sub_folder)
        file_paths: List[str] = find_files(sub_folder_path)

        # Add the new srcs and dests to the dictionary
        dict_src_dest = dict_src_dest | find_union_paths(file_paths, sub_folder_path, main_dest)

    print('Done!')

    start_threads(dict_src_dest)

    del_empty_dirs(main_path)

    print(f'\n\nTime Elapsed: {time.time() - start:.5f}')
    if not disable_input:
        input('\n\nPress Enter to continue...')


if __name__ == '__main__':
    path = [r'test']
    join_selected(path)
    print('Done')
