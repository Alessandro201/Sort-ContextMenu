import time
import os
import re
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
    'Video': {'mp4', 'wmv', 'mkv', 'mpeg', 'webm', 'flv', 'avi', '3gp'},
    'Documents': {'txt', 'docx', 'doc', 'ppt', 'pdf', 'latex'},
    'Music': {'wav', 'mp3', 'flac', 'ogg', 'aac', 'opus', 'm4a'},
    'Images': {'jpg', 'jpeg', 'png', 'raw', 'dng', 'nef', 'tiff'},
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


def replace_destination(dict_src_dest: dict[str: str], main_path: Union[str, Path], new_dest: Union[str, Path]):
    """
    Change the destination of the files. The structure is preserved but instead of being inside the main_path
    they are moved to another path, usually to avoid conflicts and messing up of the folder structure.

    """

    # Convert these paths to string to leverage str.replace()
    main_path = str(main_path)
    new_dest = str(new_dest)

    for src, dest in tqdm(dict_src_dest.items()):
        dest.replace(main_path, new_dest)
        dict_src_dest[src] = dest

    return dict_src_dest


########## SORT BY EXTENSION #############

def find_dest_paths(file_paths: List[str], main_path: Union[str, Path], main_dest: Union[str, Path],
                    main_path_name: str = ''):
    """
    Find where each file needs to be moved depending on its extension.
    The folder structure is preserved.
    """

    # Convert them to string in case they are pathlib.Path objects
    main_path = str(main_path)
    main_dest = str(main_dest)

    if main_path_name and main_path_name[-1] != ' ':
        main_path_name = main_path_name + ' '

    # dictionary containing the pair {file_path: new_path} for each file
    dict_src_dest = dict()

    for file_path in file_paths:

        # [1:] removes the dot of the extension
        _, ext = os.path.splitext(file_path)
        ext = ext[1:]

        if ext == '':  # for files like ".bash" and ".inside"
            ext = 'OTHER'

        new_folder_name = main_path_name + ext.upper()
        ext_folder: str = os.path.join(main_dest, new_folder_name)

        # Replace dest in the filename with ext_folder
        new_path = file_path.replace(main_path, ext_folder)
        dict_src_dest[file_path] = new_path

    return dict_src_dest


def sort_by_ext(main_paths, params=''):
    start = time.time()

    main_path = Path(main_paths[0])

    if params == 'inside':
        # Sort the files inside main_path and keep them there
        # Ex: parent/main_path -> parent/main_path/JPG, parent/main_path/MP3 ...
        main_dest = main_path
        main_path_name = ''

    elif params == 'outside':
        # Sort the files inside main_path and move them outside
        # Ex: parent/main_path -> parent/main_path JPG, parent/main_path MP3 ...
        main_dest = main_path.parent
        main_path_name = main_path.name

    else:
        raise ValueError(f"The \"params\" is not correct: {params}")

    print(f'SORTING BY EXTENSION.\n FOLDER TO SORT: {main_path}\n')

    print('\nSearching all the files to move, it may take a while...')
    file_paths: List[str] = find_files(main_path)
    print('Done!')

    print('\nLooking where to move the files...')
    dict_src_dest: dict = find_dest_paths(file_paths, main_path, main_dest, main_path_name)
    print('Done!')

    print('\nChecking already existing files...')
    dict_src_dest: dict = find_dest_path_without_conflicts(dict_src_dest)
    print('Done!')

    start_threads(dict_src_dest)

    del_empty_dirs(main_path)

    print(f'\n\nTime Elapsed: {time.time() - start:.5f}')
    input('\n\nPress Enter to continue...')


########## SORT BY TYPE #############


def find_dest_paths_by_type(file_paths: List[str], main_path: Union[str, Path], main_dest: Union[str, Path],
                            main_path_name: str = ''):
    """
    Find where each file needs to be moved depending on its extension.
    The folder structure is preserved.
    """

    # Convert them to string in case they are pathlib.Path objects
    main_path = str(main_path)
    main_dest = str(main_dest)

    # dictionary containing the pair {file_path: new_path} for each file
    dict_src_dest = dict()

    # If main_path_name was given but didn't end with a space add it. Later, the type of the file will be added
    # after the space
    if main_path_name and main_path_name[-1] != ' ':
        main_path_name = main_path_name + ' '

    for file_path in file_paths:

        # [1:] is needed to remove the dot of the extension
        _, ext = os.path.splitext(file_path)
        ext = ext[1:].lower()

        f_type = 'Others'
        for file_type, extensions in FILE_TYPES.items():
            if ext in extensions:
                f_type = file_type
                break

        dest_folder_name = main_path_name + f_type
        type_folder = os.path.join(main_dest, dest_folder_name)

        # Replace dest in the filename with ext_folder
        new_path = file_path.replace(main_path, type_folder)

        dict_src_dest[file_path] = new_path

    return dict_src_dest


def sort_by_type(main_paths, params=''):
    start = time.time()

    main_path = Path(main_paths[0])

    if params == 'inside':
        # Sort the files inside main_path and keep them there
        # Ex: parent/main_path -> parent/main_path/Video, parent/main_path/Audio ...
        main_dest = main_path
        main_path_name = ''

    elif params == 'outside':
        # Sort the files inside main_path and move them outside
        # Ex: parent/main_path -> parent/main_path Video, parent/main_path Audio ...
        main_dest = main_path.parent
        main_path_name = main_path.name

    else:
        raise ValueError(f"The \"params\" is not correct: {params}")

    print(f'SORTING BY TYPE.\n FOLDER TO SORT: {main_path}\n')

    print('\nSearching all the files to move, it may take a while...')
    file_paths: List[str] = find_files(main_path)
    print('Done!')

    print('\nLooking where to move the files...')
    dict_src_dest: dict = find_dest_paths_by_type(file_paths, main_path, main_dest, main_path_name)
    print('Done!')

    print('\nChecking already existing files...')
    dict_src_dest = find_dest_path_without_conflicts(dict_src_dest)
    print('Done!')

    start_threads(dict_src_dest)

    del_empty_dirs(main_path)

    print(f'\n\nTime Elapsed: {time.time() - start:.5f}')
    input('\n\nPress Enter to continue...')


########## SORT BY MODIFICATION DATE #############

def find_dest_paths_by_modification_date(file_paths: List[str], dest: Union[str, Path], strftime: str):
    """
    Find where each file needs to be moved depending on its modification date.

    """
    dest = str(dest)

    # dictionary containing the pair {file_path: new_path} for each file
    dict_src_dest = dict()

    for file_path in file_paths:
        modification_time = os.path.getmtime(file_path)
        modification_time_str = time.strftime(strftime, time.gmtime(modification_time))

        # new_dest will have the base path of dest, then it will have a new directory for each yyyy/mm/dd depending on
        # the strftime, hence from modification_time_str, and then it will have the name of the file
        new_dest = Path(dest, *modification_time_str.split(":"), Path(file_path).name)
        dict_src_dest[file_path] = str(new_dest)

    return dict_src_dest


def sort_by_modification_date(main_paths: list, params: str):
    start = time.time()

    # The destination is the same as the source
    main_path = Path(main_paths[0])
    main_dest = main_path

    # The string format is passed as params
    if params == "Y:m:d":
        strftime: str = "%Y:%m:%d"
    elif params == "Y:m":
        strftime: str = "%Y:%m"
    elif params == "Y":
        strftime: str = "%Y"
    else:
        raise ValueError(f"Wrong strftime. You need to keep it as strftime but without the '%'")

    print(f'SORTING BY FILE MODIFICATION DATE.\n FOLDER TO SORT: {main_path}\n')

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
    input('\n\nPress Enter to continue...')


########## SORT BY ACQUISITION DATE #############
def find_dest_paths_by_acquisition_date(file_paths: List[str], dest: Union[str, Path], strftime: str):
    """
    Find where each file needs to be moved depending on its acquisition date.

    """

    dest = str(dest)

    # dictionary containing the pair {file_path: new_path} for each file
    dict_src_dest = dict()

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

        # new_dest will have the base path of dest, then it will have a new directory for each yyyy/mm/dd depending on
        # the strftime, hence from acquisition_time_str, and then it will have the name of the file
        new_dest = Path(dest, *acquisition_time_str.split(":"), Path(file_path).name)
        dict_src_dest[file_path] = str(new_dest)

    return dict_src_dest


def sort_by_acquisition_date(main_paths: list, params: str):
    try:
        start = time.time()

        # The destination is the same as the source
        main_path = Path(main_paths[0])
        main_dest = main_path

        # The string format is passed as params
        if params == "Y:m:d":
            strftime: str = "%Y:%m:%d"
        elif params == "Y:m":
            strftime: str = "%Y:%m"
        elif params == "Y":
            strftime: str = "%Y"
        else:
            raise ValueError(f"Wrong strftime. You need to keep it as strftime but without the '%'")

        print(f'SORTING BY ACQUISITION DATE.\n FOLDER TO SORT: {main_path}\n')

        print('\nSearching all the files to move, it may take a while...')
        file_paths: List[str] = find_files(main_path)
        print('Done!')

        print('\nLooking where to move the files...')
        dict_src_dest: dict = find_dest_paths_by_acquisition_date(file_paths, main_dest, strftime)
        print('Done!')

        if not dict_src_dest:
            print("Unfortunately no file was found with an acquisition date.")
            input('\n\nPress Enter to continue...')
            sys.exit()

        elif len(dict_src_dest) != len(file_paths):
            print(f"\nUnfortunatly only {len(dict_src_dest)}/{len(file_paths)} files have an acquisition date. "
                  f"\nTo avoid them from tampering with already existing folders, I'll be moving them inside "
                  f'"./sorted by acquisition date/"')
            new_dest_path = Path("./sorted by acquisition date/").resolve()
            dict_src_dest = replace_destination(dict_src_dest, main_path, new_dest_path)
            print("Done")

        input('')

        print('\nChecking already existing files...')
        dict_src_dest = find_dest_path_without_conflicts(dict_src_dest)
        print('Done!')

        start_threads(dict_src_dest)

        del_empty_dirs(main_path)

        print(f'\n\nTime Elapsed: {time.time() - start:.5f}')
        input('\n\nPress Enter to continue...')
    except Exception as err:
        print(err)


########## SORT BY REGEX IN NAME #############
def find_dest_paths_by_date_in_name(file_paths: List[str], dest: Union[str, Path], strftime: str):
    """
    Find where each file needs to be moved depending on date written in the name.

    """
    dest = str(dest)

    # dictionary containing the pair {file_path: new_path} for each file
    dict_src_dest = dict()

    # Check format %Y%m%d_%H%M%S with some variations in between. If it fails try to find only the date without
    # the time
    POSSIBLE_REGEX = [re.compile('([1-2]\d\d\d)-?([0-1]\d)-?([0-3]\d)[_\-: T]?([0-2]\d):?([0-6]\d):?([0-6]\d)'),
                      re.compile('([1-2]\d\d\d)-?([0-1]\d)-?([0-3]\d)')]

    for file_path in tqdm(file_paths):

        date_match = None

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

        # new_dest will have the base path of dest, then it will have a new directory for each yyyy/mm/dd depending on
        # the strftime, hence from creation_date_str, and then it will have the name of the file
        new_dest = Path(dest, *creation_date_str.split(":"), Path(file_path).name)
        dict_src_dest[file_path] = str(new_dest)

    return dict_src_dest


def sort_by_date_in_name(main_paths: list, params=''):
    start = time.time()

    # The destination is the same as the source
    main_path = Path(main_paths[0])
    main_dest = main_path

    # The string format is passed as params
    if params == "Y:m:d":
        strftime: str = "%Y:%m:%d"
    elif params == "Y:m":
        strftime: str = "%Y:%m"
    elif params == "Y":
        strftime: str = "%Y"
    else:
        raise ValueError(f"Wrong strftime. You need to keep it as strftime but without the '%'")

    print(f'SORTING BY THE DATE WRITTEN IN THE NAME.\n FOLDER TO SORT: {main_path}\n')

    print('\nSearching all the files to move, it may take a while...')
    file_paths: List[str] = find_files(main_path)
    print('Done!')

    print('\nLooking where to move the files...')
    dict_src_dest: dict = find_dest_paths_by_date_in_name(file_paths, main_dest, strftime)
    print('Done!')

    if not dict_src_dest:
        print("Unfortunately no file was found with the date written in the title."
              "\nExiting...")
        input('')
        sys.exit()

    elif len(dict_src_dest) != len(file_paths):
        print(f"\nUnfortunatly only {len(dict_src_dest)}/{len(file_paths)} files have the date written in the title. "
              f"\nTo avoid them from tampering with already existing folders, I'll be moving them inside "
              f'"./sorted by title date/"')
        dict_src_dest = replace_destination(dict_src_dest, main_path,
                                            Path("./sorted by title date/").resolve())
        print("Done")

    print('\nChecking already existing files...')
    dict_src_dest = find_dest_path_without_conflicts(dict_src_dest)
    print('Done!')

    start_threads(dict_src_dest)

    del_empty_dirs(main_path)

    print(f'\n\nTime Elapsed: {time.time() - start:.5f}')
    input('\n\nPress Enter to continue...')


if __name__ == '__main__':
    path = [r'test']
    # sort_by_acquisition_date_ym(path)
    sort_by_ext_inside(path)
    print('Done')
