import os
import time

from tqdm import tqdm
from send2trash import send2trash
from basefunctions import *


def find_empty_dirs(dirpath):
    """
    Contextmenus needs a second argument in the functions, but it only gives an empty string

    The function search in the folder and adds to a list all the paths of folders that are empty.

    walk(folder, topdown=False) search the folder starting from the most nested one.
        If is empty it's added to dir_to_delete and only the name of the folder is added to templist.
        If it contains directories but not files,
            The program checks if the directories are all in templist, which means that they're empty.
            If it's True then the directory is added to dir_to_delete and the name of  the folder is added to templist.

    This way In dir_to_delete there are not only the empty folders, but also the folders containing only empty folders
    """

    # I choose to use a dictionary instead of a list because of its ability of instantly accessing a key,
    # instead of iterating through all elements
    to_delete = list()

    for root, dirs, files in os.walk(dirpath, topdown=False):
        if not files:
            if not dirs:
                to_delete.append(root)
            else:
                check = True
                for directory in [os.path.join(root, dir) for dir in dirs]:
                    if directory not in to_delete:
                        check = False
                        break

                if check:
                    to_delete.append(root)

    return to_delete


# def send2trash_decorator(file: str, lock):
#     try:
#         send2trash(file)
#         return file
#
#     except FileNotFoundError:
#         lock.acquire()
#         print(f' - Error: File not found: {file}\n')
#         lock.release()
#
#     except PermissionError as err:
#         lock.acquire()
#         print(f'You do not have the permission to delete: {file}\n'
#               f'- Error: {err}\n')
#         lock.release()
#
#     except OSError as err:
#         lock.acquire()
#         print(f'Error in deleting the empty dir {file}\n'
#               f'- Error: {err}\n')
#         lock.release()


def remove_folder(file_path):
    try:
        os.rmdir(file_path)
        return True

    except FileNotFoundError as err:
        print(f"FileNotFoundError in deleting {file_path}"
              f"  - Error: {err}")

    except PermissionError as err:
        print(f"PermissionError in deleting {file_path}"
              f"  - Error: {err}")

    except OSError as err:
        print(f"OSError in deleting {file_path}"
              f"  - Error: {err}")

    return False


def del_empty_dirs(main_path):
    start = time.time()

    print(f"\nSearching for empty directories to delete in: {main_path}")
    dirs_to_del = find_empty_dirs(main_path)

    if not dirs_to_del:
        print(f"No empty folders found! ({time.time() - start:.5f}s taken)")
        return

    if len(dirs_to_del) < 100:
        print(f"\nDeleting the folders...:")

        for dir in dirs_to_del:
            # Remove the folder and if it succeeded print its name
            if remove_folder(dir):
                print(f"\t{dir}")
    else:
        for dir in tqdm(dirs_to_del):
            remove_folder(dir)

    print(f"Done! Deleted {len(dirs_to_del)} empty folders! ({time.time() - start:.5f}s taken)")


def main_del_empty_dirs(main_paths, command_vars=''):
    start = time.time()

    main_path: list = clean_paths(main_paths)
    main_path: str = main_path[0]

    del_empty_dirs(main_path)

    print(f'\n\nTime Elapsed: {time.time() - start:.5f}')
    input('\n\nPress Enter to continue...')


if __name__ == "__main__":
    path = r'Test'
    del_empty_dirs(path)
    print('Done')
