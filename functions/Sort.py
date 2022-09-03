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

FILE_TYPES = {
    'Video': {'mp4', 'wmv', 'mkv', 'mpeg', 'webm', 'flv', 'avi'},
    'Documents': {'txt', 'docx', 'doc', 'ppt', 'pdf', 'latex'},
    'Music': {'wav', 'mp3', 'flac', 'ogg', 'aac', 'opus', 'm4a'},
    'Images': {'jpg', 'jpeg', 'png', 'raw', 'dng', 'nef'},
    'Archives': {'rar', 'zip', '7z', '7zip', 'tar', 'gz'},
    'Executables': {'exe', 'sh', 'msi', 'apk', 'pkg'},
}


########## BASE FUNCTIONS ################

def start_threads(dict_src_dest: Dict[Path, Path]):
    futures = list()
    lock = RLock()

    with ThreadPoolExecutor(max_workers=500) as executor:
        if len(dict_src_dest) > 100:
            disable_tqdm = False
            prt = noprint
        else:
            disable_tqdm = True
            prt = toprint

        print('\nStarting the threads... :')
        for src, dest in tqdm(dict_src_dest.items(), disable=disable_tqdm):
            make_parent_folders(dest, lock)

            th = executor.submit(move, lock, src, dest, prt)
            futures.append(th)

        if not disable_tqdm:
            print('\nWaiting for the threads to finish... :')

        for th in tqdm(as_completed(futures), disable=disable_tqdm):
            th.result()


def replace_destination(dict_src_dest: dict[str: str], main_path: str, new_dest: Path):
    """
    Change the destination of the files. The structure is preserved but instead of being inside the main_path
    they are moved to another path, usually to avoid conflicts and messing up of the folder structure.

    """
    new_dest = str(new_dest)

    for src, dest in tqdm(dict_src_dest.items()):
        dest.replace(main_path, new_dest)
        dict_src_dest[src] = dest

    return dict_src_dest


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

    print('\nChecking already existing files...')
    dict_src_dest: dict = find_dest_path_without_conflicts(dict_src_dest)
    print('Done!')

    start_threads(dict_src_dest)

    del_empty_dirs(main_path)

    print(f'\n\nTime Elapsed: {time.time() - start:.5f}')


########## SORT BY TYPE #############


def find_dest_paths_by_type(file_paths: List[str], main_path: str, main_dest: str, main_folder_name: str = ''):
    """
    Find where each file needs to be moved depending on its extension.
    The folder structure is preserved.
    """

    # dictionary containing the pair {file_path: new_path} for each file
    dict_src_dest = dict()

    # dictionary containing the name of the folder {file type: type_folder}
    folders_by_type = dict()

    # all files, this is needed to check beforehand for name conflicts
    files_by_type = dict()

    for file_path in file_paths:

        # [1:] is needed to remove the dot of the extension
        _, ext = os.path.splitext(file_path)
        ext = ext[1:].lower()

        for file_type, extensions in FILE_TYPES.items():
            if ext in extensions:
                f_type = file_type
                break
        else:
            f_type = 'Others'

        if f_type in folders_by_type:
            dest_folder: str = folders_by_type[f_type]
        else:
            dest_folder: str = os.path.join(main_dest, main_folder_name + f_type)
            folders_by_type[f_type] = dest_folder

        # Replace dest in the filename with ext_folder
        new_path = file_path.replace(main_path, dest_folder)

        dict_src_dest[file_path] = new_path

    return dict_src_dest


def sort_by_type_inside(main_paths, command_vars=''):
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

    sort_by_type(main_path, main_dest)

    print(f'\n\nTime Elapsed: {time.time() - start:.5f}')
    input('\n\nPress Enter to continue...')


def sort_by_type_outside(main_paths, command_vars=''):
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

    sort_by_type(main_path, main_dest, main_folder_name)

    print(f'\n\nTime Elapsed: {time.time() - start:.5f}')
    input('\n\nPress Enter to continue...')


def sort_by_type(main_path, main_dest, main_folder_name=''):
    start = time.time()

    print(f'Main folder: {main_path}\n')

    print('\nSearching all the files to move, it may take a while...')
    file_paths: List[str] = find_files(main_path)
    print('Done!')

    print('\nLooking where to move the files...')
    dict_src_dest: dict = find_dest_paths_by_type(file_paths, main_path, main_dest, main_folder_name)
    print('Done!')

    print('\nChecking already existing files...')
    dict_src_dest = find_dest_path_without_conflicts(dict_src_dest)
    print('Done!')

    start_threads(dict_src_dest)

    del_empty_dirs(main_path)

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

    print(f'Main folder: {main_path}\n')

    print('\nSearching all the files to move, it may take a while...')
    file_paths: List[str] = find_files(main_path)
    print('Done!')

    print('\nLooking where to move the files...')
    dict_src_dest: dict = find_dest_paths_by_modification_date(file_paths, main_dest, strftime)
    print('Done!')

    print('\nChecking already existing files...')
    dict_src_dest = find_dest_path_without_conflicts(dict_src_dest)
    print('Done!')

    start_threads(dict_src_dest)

    del_empty_dirs(main_path)

    print(f'\n\nTime Elapsed: {time.time() - start:.5f}')


def sort_by_modification_date_ymd(main_paths: list, command_vars=''):
    start = time.time()

    main_path: list = clean_paths(main_paths)
    main_path: str = main_path[0]

    sort_by_modification_date(main_path, "%Y:%m:%d")

    print(f'\n\nTime Elapsed: {time.time() - start:.5f}')
    input('\n\nPress Enter to continue...')


def sort_by_modification_date_ym(main_paths: list, command_vars=''):
    start = time.time()

    main_path: list = clean_paths(main_paths)
    main_path: str = main_path[0]

    sort_by_modification_date(main_path, "%Y:%m")

    print(f'\n\nTime Elapsed: {time.time() - start:.5f}')
    input('\n\nPress Enter to continue...')


def sort_by_modification_date_y(main_paths: list, command_vars=''):
    start = time.time()

    main_path: list = clean_paths(main_paths)
    main_path: str = main_path[0]

    sort_by_modification_date(main_path, "%Y")

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

    print(f'Main folder: {main_path}\n')

    print('\nSearching all the files to move, it may take a while...')
    file_paths: List[str] = find_files(main_path)
    print('Done!')

    print('\nLooking where to move the files...')
    dict_src_dest: dict = find_dest_paths_by_acquisition_date(file_paths, main_dest, strftime)
    print('Done!')

    if not dict_src_dest:
        print("Unfortunately no file was found with an acquisition date."
              "\nExiting...")
        return

    elif len(dict_src_dest) != len(file_paths):
        print(f"\nUnfortunatly only {len(dict_src_dest)}/{len(file_paths)} files have an acquisition date. "
              f"\nTo avoid them from tampering with already existing folders, I'll be moving them inside "
              f'"./acquisition sorted/"')
        dict_src_dest = replace_destination(dict_src_dest, main_path, Path("./acquisition sorted/").resolve())
        print("Done")

    print('\nChecking already existing files...')
    dict_src_dest = find_dest_path_without_conflicts(dict_src_dest)
    print('Done!')

    start_threads(dict_src_dest)

    del_empty_dirs(main_path)

    print(f'\n\nTime Elapsed: {time.time() - start:.5f}')


def sort_by_acquisition_date_ymd(main_paths: list, command_vars=''):
    start = time.time()

    main_path: list = clean_paths(main_paths)
    main_path: str = main_path[0]

    sort_by_acquisition_date(main_path, "%Y:%m:%d")

    print(f'\n\nTime Elapsed: {time.time() - start:.5f}')
    input('\n\nPress Enter to continue...')


def sort_by_acquisition_date_ym(main_paths: list, command_vars=''):
    start = time.time()

    main_path: list = clean_paths(main_paths)
    main_path: str = main_path[0]

    sort_by_acquisition_date(main_path, "%Y:%m")

    print(f'\n\nTime Elapsed: {time.time() - start:.5f}')
    input('\n\nPress Enter to continue...')


def sort_by_acquisition_date_y(main_paths: list, command_vars=''):
    start = time.time()

    main_path: list = clean_paths(main_paths)
    main_path: str = main_path[0]

    sort_by_acquisition_date(main_path, "%Y")

    print(f'\n\nTime Elapsed: {time.time() - start:.5f}')
    input('\n\nPress Enter to continue...')


########## SORT BY REGEX IN NAME #############
def find_dest_paths_by_date_in_name(file_paths: List[str], dest: str, strftime: str):
    """
    Find where each file needs to be moved depending on date written in the name.

    """
    import re

    # dictionary containing the pair {file_path: new_path} for each file
    dict_src_dest = dict()

    # dictionary containing the pair {date: date_folder} for every date found
    dates = dict()

    # Check format %Y%m%d_%H%M%S with some variations in between. If it fails try to find only the date without
    # the time
    POSSIBLE_REGEX = [re.compile('([1-2]\d\d\d)-?([0-1]\d)-?([0-3]\d)[_\-: ]?([0-2]\d):?([0-6]\d):?([0-6]\d)'),
                      re.compile('([1-2]\d\d\d)-?([0-1]\d)-?([0-3]\d)')]

    for file_path in tqdm(file_paths):

        # Try subsequently all possible regex patterns. If a match is found then go on, otherwise try the next pattern.
        # If all patterns have been tried but no match was found then skip this file
        for regex_pattern in POSSIBLE_REGEX:
            date_match = regex_pattern.search(os.path.basename(file_path))

            if date_match:
                break

        if not date_match:
            continue

        # This part that seems unnecessary allows this function to be a bit more generic and be called
        # by sort_by_date_in_name_* functions with their own strftime, while at the same time
        # Preserving the power of regex that strptime doesn't have.
        if len(date_match.groups()) == 6:
            year, month, day, hour, minutes, seconds = date_match.groups()
            creation_date_str = f'{year}-{month}-{day}_{hour}:{minutes}:{seconds}'
            creation_date_struct_object = time.strptime(creation_date_str, '%Y-%m-%d_%H:%M:%S')
        else:
            year, month, day = date_match.groups()
            creation_date_str = f'{year}-{month}-{day}'
            creation_date_struct_object = time.strptime(creation_date_str, '%Y-%m-%d')

        creation_date_str = time.strftime(strftime, creation_date_struct_object)

        if creation_date_str in dates:
            new_dest = dates[creation_date_str]
        else:

            # todo: Can be quickend and cleaned with pathlib.mkdir(parents=True, exists_ok=True)
            new_dest = dest
            for new_folder in creation_date_str.split(":"):
                new_dest = os.path.join(new_dest, new_folder)

            dates[creation_date_str] = new_dest

        filename = os.path.basename(file_path)
        dict_src_dest[file_path] = os.path.join(new_dest, filename)

    return dict_src_dest


def sort_by_date_in_name(main_path: str, strftime: str):
    start = time.time()

    main_dest = main_path

    print(f'Main folder: {main_path}\n')

    print('\nSearching all the files to move, it may take a while...')
    file_paths: List[str] = find_files(main_path)
    print('Done!')

    print('\nLooking where to move the files...')
    dict_src_dest: dict = find_dest_paths_by_date_in_name(file_paths, main_dest, strftime)
    print('Done!')

    if not dict_src_dest:
        print("Unfortunately no file was found with a media creation date."
              "\nExiting...")
        return

    elif len(dict_src_dest) != len(file_paths):
        print(f"\nUnfortunatly only {len(dict_src_dest)}/{len(file_paths)} files have a media creation date. "
              f"\nTo avoid them from tampering with already existing folders, I'll be moving them inside "
              f'"./sorted by media creation date/"')
        dict_src_dest = replace_destination(dict_src_dest, main_path,
                                            Path("./sorted by media creation date/").resolve())
        print("Done")

    print('\nChecking already existing files...')
    dict_src_dest = find_dest_path_without_conflicts(dict_src_dest)
    print('Done!')

    start_threads(dict_src_dest)

    del_empty_dirs(main_path)

    print(f'\n\nTime Elapsed: {time.time() - start:.5f}')


def sort_by_date_in_name_ymd(main_paths: list, command_vars=''):
    start = time.time()

    main_path: list = clean_paths(main_paths)
    main_path: str = main_path[0]

    sort_by_date_in_name(main_path, "%Y:%m:%d")

    print(f'\n\nTime Elapsed: {time.time() - start:.5f}')
    input('\n\nPress Enter to continue...')


def sort_by_date_in_name_ym(main_paths: list, command_vars=''):
    start = time.time()

    main_path: list = clean_paths(main_paths)
    main_path: str = main_path[0]

    sort_by_date_in_name(main_path, "%Y:%m")

    print(f'\n\nTime Elapsed: {time.time() - start:.5f}')
    input('\n\nPress Enter to continue...')


def sort_by_date_in_name_y(main_paths: list, command_vars=''):
    start = time.time()

    main_path: list = clean_paths(main_paths)
    main_path: str = main_path[0]

    sort_by_date_in_name(main_path, "%Y")

    print(f'\n\nTime Elapsed: {time.time() - start:.5f}')
    input('\n\nPress Enter to continue...')


if __name__ == '__main__':
    path = [r'test']
    # sort_by_acquisition_date_ym(path)
    sort_by_ext_inside(path)
    print('Done')
