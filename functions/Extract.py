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


def find_dest_paths(file_paths: List[str], main_dest: Union[str, Path]):
    """
    Find the destination of each file.
    """

    # Convert it to string in case it's a pathlib.Path object
    main_dest = str(main_dest)

    # dictionary containing the pair {file_path: dest_path} for each file
    dict_src_dest = dict()

    for file_path in file_paths:
        # Find the name of the file and add it to the destination
        filename = os.path.basename(file_path)
        dest = os.path.join(main_dest, filename)

        dict_src_dest[file_path] = dest

    return dict_src_dest


def extract_all(main_paths, params=''):
    start = time.time()

    main_path = Path(main_paths[0])

    if params == 'inside':
        # Sort the files inside main_path and keep them there
        # Ex: parent/main_path -> parent/main_path/JPG, parent/main_path/MP3 ...
        main_dest = main_path

    elif params == 'outside':
        # Sort the files inside main_path and move them outside
        # Ex: parent/main_path -> parent/main_path JPG, parent/main_path MP3 ...
        main_dest = main_path.parent

    else:
        raise ValueError(f"The \"params\" is not correct: {params}")

    print(f'EXTRACTING ALL FILES FROM: {main_path}\n')

    print('\nSearching all the files... it may take a while...')
    file_paths: list = find_files(main_path, skip_files_in_main_folder=True)
    print('Done!')

    print('\nLooking where to move the files...')
    dict_src_dest: dict = find_dest_paths(file_paths, main_dest)
    print('Done!')

    print('\nResolving any conflicts and duplicated names...')
    dict_src_dest: dict = remove_unnecessary_moves(dict_src_dest)
    dict_src_dest: dict = find_dest_path_without_conflicts(dict_src_dest)
    print('Done!')

    ##### DRY RUN ENABLED #####
    if os.path.exists(main_path / "ENABLE_DRY_RUN"):
        print_src_dest(dict_src_dest)
        print(f'\n\nTime Elapsed: {time.time() - start:.5f} seconds')
        input('Press Enter to continue...')
        sys.exit()

    start_threads(dict_src_dest)

    del_empty_dirs(main_path)

    print(f'\n\nTime Elapsed: {time.time() - start:.5f} seconds')
    input('Press Enter to continue...')


if __name__ == "__main__":
    pass
    print('Done')
