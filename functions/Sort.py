import time
import os
import exifread
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import RLock
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm

from basefunctions import *
from Delete import *
from Extract import *

import basefunctions


########## BASE FUNCTIONS ################

def start_threads(dict_src_dest: Dict[Path, Path]):
    futures = list()
    lock = RLock()

    with ThreadPoolExecutor(max_workers=100) as executor:
        if len(dict_src_dest) > 100:
            dis = False
            prt = basefunctions.noprint
        else:
            dis = True
            prt = basefunctions.toprint

        print('Loading the threads... :')
        for src, dest in tqdm(dict_src_dest.items(), disable=dis):
            make_parent_folders(dest, lock)

            th = executor.submit(move, lock, src, dest, prt)
            futures.append(th)

        if not dis:
            print('\nWaiting for threads to finish... :')

        for th in tqdm(as_completed(futures), disable=dis):
            th.result()


########## OLD CODE TO BE REMOVED - SORT BY EXTENSION #############

# def find_dest_paths_old(file_paths: List[str], dest: str):
#     """
#     Find where each file needs to be moved depending on its extension.
#     The folder structure is preserved.
#     """
#
#     # dictionary containing the pair {file_path: new_path} for each file
#     dict_src_dest = dict()
#
#     # dictionary containing the pair {extension: extension_folder} for every extension found
#     extensions = dict()
#
#     for file_path in file_paths:
#
#         # [1:] is needed to remove the dot of the extension
#         _, ext = os.path.splitext(file_path)
#         ext = ext[1:]
#
#         # Folder which will contain all the files with ext as extension.
#         # It has the same name of dest but with the ext added
#         if ext in extensions:
#             ext_folder: str = extensions[ext]
#         else:
#             if ext == '':  # for files like ".bash" and ".inside"
#                 ext = 'OTHER'
#             ext_folder: str = dest + ' ' + ext.upper()
#             extensions[ext] = ext_folder
#
#         # Replace dest in the filename with ext_folder
#         new_path = file_path.replace(dest, ext_folder)
#
#         dict_src_dest[file_path] = new_path
#
#     return dict_src_dest
#
#
# def sort_by_ext_inside_old(main_paths, command_vars=''):
#     start = time.time()
#
#     main_paths: list = clean_paths(main_paths)
#     main_path: str = main_paths[0]
#
#     print(f"Sorting by extensions the contents of {main_path}")
#     files = list()
#     for sub_folder in os.listdir(main_path):
#         sub_folder_path = os.path.join(main_path, sub_folder)
#         if os.path.isdir(sub_folder_path):
#             print(f'\n\n\n########## WORKING ON THE FOLDER: {sub_folder_path} ##########\n')
#
#             sort_by_ext(main_path=sub_folder_path)
#         else:
#             files.append(sub_folder_path)
#
#     # I need to take care of the files which are not in any sub folder
#
#     print("Done!")
#     print(f'\n\nTime Elapsed: {time.time() - start:.5f}')
#
#     del_empty_dirs(main_path)
#
#     input('\n\nPress Enter to continue...')
#
#
# def sort_by_ext_outside_old(main_paths, command_vars=''):
#     start = time.time()
#
#     main_path: list = clean_paths(main_paths)
#     main_path: str = main_path[0]
#
#     sort_by_ext(main_path)
#
#     del_empty_dirs(main_path)
#
#     print(f'\n\nTime Elapsed: {time.time() - start:.5f}')
#     input('\n\nPress Enter to continue...')
#
#
# def sort_by_ext_old(main_path):
#     start = time.time()
#
#     main_dest = main_path
#
#     print(f'Main folder: {main_path}\n')
#
#     print('\nSearching all the files to move, it may take a while...')
#     file_paths: List[str] = find_files(main_path)
#     print('Done!')
#
#     print('\nLooking where to move the files...')
#     dict_src_dest: dict = find_dest_paths(file_paths, main_dest)
#     print('Done!')
#
#     start_threads(dict_src_dest)
#
#     print(f'\n\nTime Elapsed: {time.time() - start:.5f}')
#

########## SORT BY EXTENSION #############

def find_dest_paths(file_paths: List[str], main_path: str, main_dest: str, main_folder_name: str = ''):
    """
    Find where each file needs to be moved depending on its extension.
    The folder structure is preserved.
    """

    # dictionary containing the pair {file_path: new_path} for each file
    dict_src_dest = dict()

    # dictionary containing the pair {extension: extension_folder} for every extension found
    extensions = dict()

    for file_path in file_paths:

        # [1:] is needed to remove the dot of the extension
        _, ext = os.path.splitext(file_path)
        ext = ext[1:]

        # Folder which will contain all the files with ext as extension.
        # It has the same name of dest but with the ext added
        if ext in extensions:
            ext_folder: str = extensions[ext]
        else:
            if ext == '':  # for files like ".bash" and ".inside"
                ext = 'OTHER'

            # ext_folder: str = dest + ' ' + ext.upper()
            ext_folder: str = os.path.join(main_dest, main_folder_name + ext.upper())
            extensions[ext] = ext_folder

        # Replace dest in the filename with ext_folder
        new_path = file_path.replace(main_path, ext_folder)

        dict_src_dest[file_path] = new_path

    return dict_src_dest


# todo: fix
def sort_by_ext_inside(main_paths, command_vars=''):
    """
    All the files inside main_path (found recursively) will be divided by their extensions
    preserving the folder structure.

    Ex:
        main:
            - file_main1.txt
            - folder1
                - file_inside1.txt
                - file_inside2.mp3

    main_path = main

    Result:
        main:
            - TXT
                - file_main1.txt
                - folder1
                    - file_inside1.txt
            - MP3
                - folder1
                    - file_inside2.mp3

    """

    start = time.time()

    main_path: list = clean_paths(main_paths)
    main_path: str = main_path[0]

    main_dest = main_path

    sort_by_ext(main_path, main_dest)

    del_empty_dirs(main_path)

    print(f'\n\nTime Elapsed: {time.time() - start:.5f}')
    input('\n\nPress Enter to continue...')


def sort_by_ext_outside(main_paths, command_vars=''):
    """
    Ex:
        main:
            - file_main1.txt
            - folder1
                - file_inside1.txt
                - file_inside2.mp3

    main_path = folder1

    Result:
        main:
            - file_main1.txt
            - folder1 TXT
                - file_inside1.txt
            - folder1 MP3
                - file_inside2.mp3

    """

    start = time.time()

    main_path: list = clean_paths(main_paths)
    main_path: str = main_path[0]

    main_dest = Path(main_path).parent
    main_folder_name = Path(main_path).name + ' '

    sort_by_ext(main_path, main_dest, main_folder_name)

    del_empty_dirs(main_path)

    print(f'\n\nTime Elapsed: {time.time() - start:.5f}')
    input('\n\nPress Enter to continue...')


def sort_by_ext(main_path, main_dest, main_folder_name=''):
    start = time.time()

    print(f'Main folder: {main_path}\n')

    print('\nSearching all the files to move, it may take a while...')
    file_paths: List[str] = find_files(main_path)
    print('Done!')

    print('\nLooking where to move the files...')
    dict_src_dest: dict = find_dest_paths(file_paths, main_path, main_dest, main_folder_name)
    print('Done!')

    start_threads(dict_src_dest)

    print(f'\n\nTime Elapsed: {time.time() - start:.5f}')


########## SORT BY MODIFICATION DATE #############

def find_dest_paths_by_modification_date(file_paths: List[str], dest: str, strftime: str):
    """
    Find where each file needs to be moved depending on its modification date.

    """

    # dictionary containing the pair {file_path: new_path} for each file
    dict_src_dest = dict()

    # dictionary containing the pair {extension: extension_folder} for every extension found
    dates = dict()

    for file_path in file_paths:

        mod_time = os.path.getmtime(file_path)
        mod_time_str = time.strftime(strftime, time.gmtime(mod_time))

        if mod_time_str in dates:
            new_dest = dates[mod_time_str]
        else:
            new_dest = dest
            for new_folder in mod_time_str.split(":"):
                new_dest = os.path.join(new_dest, new_folder)

            dates[mod_time_str] = new_dest

        filename = os.path.basename(file_path)
        dict_src_dest[file_path] = os.path.join(new_dest, filename)

    return dict_src_dest


def sort_by_modification_date(main_path: str, strftime: str):
    start = time.time()

    main_dest = main_path

    print('\nSearching all the files to move, it may take a while...')
    file_paths: List[str] = find_files(main_path)
    print('Done!')

    print('\nLooking where to move the files...')
    dict_src_dest: dict = find_dest_paths_by_modification_date(file_paths, main_dest, strftime)
    print('Done!')

    start_threads(dict_src_dest)

    print(f'\n\nTime Elapsed: {time.time() - start:.5f}')


def sort_by_modification_date_ymd(main_paths: list, command_vars=''):
    start = time.time()

    main_path: list = clean_paths(main_paths)
    main_path: str = main_path[0]

    print(f'Main folder: {main_path}\n')

    sort_by_modification_date(main_path, "%Y:%m:%d")

    del_empty_dirs(main_path)

    print(f'\n\nTime Elapsed: {time.time() - start:.5f}')
    input('\n\nPress Enter to continue...')


def sort_by_modification_date_ym(main_paths: list, command_vars=''):
    start = time.time()

    main_path: list = clean_paths(main_paths)
    main_path: str = main_path[0]

    print(f'Main folder: {main_path}\n')

    sort_by_modification_date(main_path, "%Y:%m")

    del_empty_dirs(main_path)

    print(f'\n\nTime Elapsed: {time.time() - start:.5f}')
    input('\n\nPress Enter to continue...')


def sort_by_modification_date_y(main_paths: list, command_vars=''):
    start = time.time()

    main_path: list = clean_paths(main_paths)
    main_path: str = main_path[0]

    print(f'Main folder: {main_path}\n')

    sort_by_modification_date(main_path, "%Y")

    del_empty_dirs(main_path)

    print(f'\n\nTime Elapsed: {time.time() - start:.5f}')
    input('\n\nPress Enter to continue...')


########## SORT BY ACQUISITION DATE #############

def find_dest_paths_by_acquisition_date(file_paths: List[str], dest: str, strftime: str):
    """
    Find where each file needs to be moved depending on its acquisition date.

    """

    # dictionary containing the pair {file_path: new_path} for each file
    dict_src_dest = dict()

    # dictionary containing the pair {date: date_folder} for every date found
    dates = dict()

    for file_path in tqdm(file_paths):
        try:
            with open(file_path, "rb") as f:
                # details=False avoid loading the thumbnail and processing makernote tags
                # stop_tag stops the processing of exif files when the given tag is reached
                tags = exifread.process_file(f, details=False)
        except exifread.struct.error:
            pass

        # Try getting acquisition date
        if "Image DateTime" in tags:
            struct_time_object = time.strptime(str(tags['Image DateTime']), "%Y:%m:%d %H:%M:%S")
            acquisition_time_str = time.strftime(strftime, struct_time_object)

        # If the acquisition date is not present then skip to the next image
        else:

            continue

        if acquisition_time_str in dates:
            new_dest = dates[acquisition_time_str]
        else:
            new_dest = dest
            for new_folder in acquisition_time_str.split(":"):
                new_dest = os.path.join(new_dest, new_folder)

            dates[acquisition_time_str] = new_dest

        filename = os.path.basename(file_path)
        dict_src_dest[file_path] = os.path.join(new_dest, filename)

    return dict_src_dest


def sort_by_acquisition_date(main_path: str, strftime: str):
    start = time.time()

    main_dest = main_path

    print('\nSearching all the files to move, it may take a while...')
    file_paths: List[str] = find_files(main_path)
    print('Done!')

    print('\nLooking where to move the files...')
    dict_src_dest: dict = find_dest_paths_by_acquisition_date(file_paths, main_dest, strftime)
    print('Done!')

    start_threads(dict_src_dest)

    print(f'\n\nTime Elapsed: {time.time() - start:.5f}')


def sort_by_acquisition_date_ymd(main_paths: list, command_vars=''):
    start = time.time()

    main_path: list = clean_paths(main_paths)
    main_path: str = main_path[0]

    print(f'Main folder: {main_path}\n')

    sort_by_acquisition_date(main_path, "%Y:%m:%d")

    del_empty_dirs(main_path)

    print(f'\n\nTime Elapsed: {time.time() - start:.5f}')
    input('\n\nPress Enter to continue...')


def sort_by_acquisition_date_ym(main_paths: list, command_vars=''):
    start = time.time()

    main_path: list = clean_paths(main_paths)
    main_path: str = main_path[0]

    print(f'Main folder: {main_path}\n')

    sort_by_acquisition_date(main_path, "%Y:%m")

    del_empty_dirs(main_path)

    print(f'\n\nTime Elapsed: {time.time() - start:.5f}')
    input('\n\nPress Enter to continue...')


def sort_by_acquisition_date_y(main_paths: list, command_vars=''):
    start = time.time()

    main_path: list = clean_paths(main_paths)
    main_path: str = main_path[0]

    print(f'Main folder: {main_path}\n')

    sort_by_acquisition_date(main_path, "%Y")

    del_empty_dirs(main_path)

    print(f'\n\nTime Elapsed: {time.time() - start:.5f}')
    input('\n\nPress Enter to continue...')


if __name__ == '__main__':
    path = [r'C:\Users\AlessandroUser\Desktop\Foto papa oneplus - Copy\WhatsApp\Media']
    # sort_by_acquisition_date_ym(path)
    sort_by_ext_inside(path)
    print('Done')
