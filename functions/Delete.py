import os
from pathlib import Path
import time
import stat

from tqdm import tqdm
from send2trash import send2trash
from basefunctions import *


def find_empty_dirs(dirpath):
    """
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
    dirs_to_delete = list()

    for root, dirs, files in os.walk(dirpath, topdown=False):
        if not files:
            if not dirs:
                dirs_to_delete.append(root)
            else:
                dirs_fullpath = [os.path.join(root, directory) for directory in dirs]

                # If all the directories in root are empty directories (hence to be deleted)
                # then add it to dirs_to_delete
                if all(directory in dirs_to_delete for directory in dirs_fullpath):
                    dirs_to_delete.append(root)

    return dirs_to_delete


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


def remove_folder(file_path, first_try=True):
    try:
        os.rmdir(file_path)
        return True

    except FileNotFoundError as err:
        print(f"FileNotFoundError in deleting {file_path}"
              f"  - Error: {err}")

    except PermissionError as err:
        if first_try:
            # Sometimes some folders get a stubborn read-only attribute which inhibits
            # os.rmdir from removing the directory. Changing the file permission should
            # do the trick

            # Change folder permissions to 0777:
            # stat.S_IRWXU Mask for file owner permissions.
            # stat.S_IRWXG Mask for group permissions.
            # stat.S_IRWXO Mask for permissions for others (not in group).
            print(
                f"PermissionErrors encountered in deleting a folder. Trying to change file permissions on {file_path}")
            os.chmod(file_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            return remove_folder(file_path, first_try=False)

        else:
            print(f"PermissionError encountered again in deleting {file_path}"
                  f"  - Error: {err}")

    except OSError as err:
        print(f"OSError in deleting {file_path}"
              f"  - Error: {err}")

    return False


def del_empty_dirs(main_path):
    start = time.time()

    print(f'SEARCHING FOR EMPTY DIRECTORIES TO DELETE IN: {main_path}\n')
    dirs_to_delete = find_empty_dirs(main_path)

    if not dirs_to_delete:
        print(f"No empty folders found! ({time.time() - start:.5f}s taken)")
        return

    print(f"\nDeleting the folders...")
    if len(dirs_to_delete) < 100:
        for directory in dirs_to_delete:
            # Remove the folder and if it succeeded print its name
            if remove_folder(directory):
                print(f"\t{directory}")
    else:
        for directory in tqdm(dirs_to_delete):
            remove_folder(directory)

    print(f"Done! Deleted {len(dirs_to_delete)} empty folders! ({time.time() - start:.5f}s taken)")


def main_del_empty_dirs(main_paths, command_vars=''):
    start = time.time()

    main_path = Path(main_paths[0])

    del_empty_dirs(main_path)

    print(f'\n\nTime Elapsed: {time.time() - start:.5f}')
    input('\n\nPress Enter to continue...')


if __name__ == "__main__":
    path = r'Test'
    del_empty_dirs(path)
    print('Done')
