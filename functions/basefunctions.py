import os
import shutil
import sys
from pathlib import Path
from typing import Union

from context_menu import menus
from tqdm import tqdm


def clear_menus():
    try:
        menus.removeMenu('SORT', type='DIRECTORY')
        menus.removeMenu('SORT', type='DIRECTORY_BACKGROUND')
        menus.removeMenu('SORT', type='FILES')
    except FileNotFoundError:
        # It's likely because one of the menus specified above is not implemented
        pass


def toprint(lock, text):
    lock.acquire()
    print(text)
    lock.release()


def noprint(*args):
    pass


def find_files(folder_path, skip_files_in_main_folder=False):
    paths = []
    for root, dirs, files in os.walk(folder_path):
        if skip_files_in_main_folder and root == folder_path:
            continue

        for file in files:
            file_path = os.path.join(root, file)
            paths.append(file_path)

    return paths


def find_num(name):
    i = name.rfind('(')
    j = name.rfind(')')

    if i != -1 and j == (len(name) - 1):
        try:
            num = int(name[i + 1: -1])

        except ValueError:
            num = 0
            i = len(name)
    else:
        num = 0
        i = len(name)

    return i, num


def remove_unnecessary_moves(dict_src_dest: dict):
    """
    If the source file is already in the destination folder it doesn't need to be moved, so it's removed.
    """

    new_dict_src_dest = dict()

    for src, dest in dict_src_dest.items():
        if not dest == src:
            new_dict_src_dest[src] = dest

    return new_dict_src_dest


def find_dest_path_without_conflicts(dict_src_dest: dict):
    # It's needed to check for redundancies in the names
    path_checked = set()

    for src, dest in tqdm(dict_src_dest.items()):
        # If the source file is already in the destination folder it doesn't need any renaming
        # It also means that the file exists already, so you don't need to add it to path_checked
        # because it's caught by os.path.exists()
        if dest == src:
            continue

        basename, filename = os.path.split(dest)

        name, ext = os.path.splitext(filename)
        i, num = find_num(name)

        while dest in path_checked or os.path.exists(dest):
            num += 1
            dest_name = name[:i] + '(' + str(num) + ')' + ext
            dest = os.path.join(basename, dest_name)

        path_checked.add(dest)
        dict_src_dest[src] = dest

    return dict_src_dest


def move(lock, src, dest, prt):
    try:
        shutil.move(src, dest)

        prt(lock, f'{src} \t--> {dest}')

    except PermissionError as err:
        lock.acquire()
        print(f'You do not have the permission to move {src}\n'
              f'- Error: {err}\n')
        lock.release()

    except OSError as err:
        lock.acquire()
        print(f'OSError in moving: {src}\n'
              f'- Error: {err}\n')
        lock.release()


def make_parent_folders(filepath: Union[str, Path], lock=None):
    """
    Create the parent folders if they do not exist
    """

    try:
        if lock:
            lock.acquire()

        if type(filepath) == Path:
            os.makedirs(filepath.parent, exist_ok=True)
        else:
            parent_folder = os.path.dirname(filepath)
            os.makedirs(parent_folder, exist_ok=True)

    except PermissionError as err:
        print(f'You do not have the permission to create all the parent folders of {filepath}\n'
              f'- Error: {err}\n')
        input("\n\nPress Enter to exit...")
        sys.exit()

    except OSError as err:
        print(f'Error in creating the directory: {filepath}. \n'
              f'- Error: {err}\n')
        input("\n\nPress Enter to exit...")
        sys.exit()

    except Exception as err:
        print(f'Fatal Exception: {err}\n')
        input("\n\nPress Enter to exit...")
        sys.exit()

    finally:
        if lock:
            lock.release()


def set_dry_run(main_paths: list, params=''):

    main_path = Path(main_paths[0])
    dry_run = False

    if params.lower() == 'true':
        dry_run = True

    if dry_run:
        with open(main_path / 'ENABLE_DRY_RUN', 'w') as f:
            f.write("ENABLED")

        input("Done! Dry run ENABLED! \nRun the scripts ONLY FROM THIS FOLDER to have the dry run enabled!!!")
    else:
        try:
            os.remove(main_path / "ENABLE_DRY_RUN")
        except FileNotFoundError:
            pass
        except OSError as err:
            input(f"Error in removing ./ENABLE_DRY_RUN: {err}")
            sys.exit()

        input("Done! Dry run DISABLED for this folder!")


def print_src_dest(files_src_dest: dict):
    for src, dest in files_src_dest.items():
        print(f"{src} \t->  {dest}")
