from context_menu import menus

from functions.basefunctions import clear_menus, set_dry_run
from functions.Extract import extract_all
from functions.Delete import main_del_empty_dirs
from functions.Sort import *

if __name__ == '__main__':
    # CLEAR PREVIOUS MENUS
    clear_menus()
    print("Previous context menu cleaned")

    # SORT CONTEXT MENU
    sortcm = menus.ContextMenu("Sort by date")

    # Windows registry (I think) doesn't allow to have "%" in the params variable.
    # As such it will be converted inside the function
    sortcm.add_items(
        [menus.ContextCommand('Modification date yyyy/mm/dd', python=sort_by_modification_date, params="Y:m:d"),
         menus.ContextCommand('Modification date yyyy/mm', python=sort_by_modification_date, params="Y:m"),
         menus.ContextCommand('Modification date yyyy', python=sort_by_modification_date, params="Y"),
         menus.ContextCommand('Acquisition date yyyy/mm/dd', python=sort_by_acquisition_date, params="Y:m:d"),
         menus.ContextCommand('Acquisition date yyyy/mm', python=sort_by_acquisition_date, params="Y:m"),
         menus.ContextCommand('Acquisition date yyyy', python=sort_by_acquisition_date, params="Y"),
         menus.ContextCommand('Date written in the name yyyy/mm/dd', python=sort_by_date_in_name, params="Y:m:d"),
         menus.ContextCommand('Date written in the name yyyy/mm', python=sort_by_date_in_name, params="Y:m"),
         menus.ContextCommand('Date written in the name yyyy', python=sort_by_date_in_name, params="Y"),
         ])

    # DIRECTORY CONTEXT MENU
    dircm = menus.ContextMenu('SORT', type='DIRECTORY')

    dircm.add_items(
        [menus.ContextCommand('Extract all inside', python=extract_all, params='inside'),
         menus.ContextCommand('Extract all outside', python=extract_all, params='outside'),
         menus.ContextCommand('Sort by Extension inside', python=sort_by_ext, params='inside'),
         menus.ContextCommand('Sort by Extension outside', python=sort_by_ext, params='outside'),
         menus.ContextCommand('Sort by Type inside', python=sort_by_type, params='inside'),
         menus.ContextCommand('Sort by Type outside', python=sort_by_type, params='outside'),
         sortcm,
         menus.ContextCommand('Delete empty directories inside', python=main_del_empty_dirs),
         menus.ContextCommand('Enable dry run', python=set_dry_run, params='True'),
         menus.ContextCommand('Disable dry run', python=set_dry_run, params='False')
         ])

    dircm.compile()

    # DIRECTORY_BACKGROUND CONTEXT MENU
    bgcm = menus.ContextMenu('SORT', type='DIRECTORY_BACKGROUND')

    bgcm.add_items([
        menus.ContextCommand('Extract all', python=extract_all, params='inside'),
        menus.ContextCommand('Sort by Extension', python=sort_by_ext, params='inside'),
        menus.ContextCommand('Sort by Type', python=sort_by_type, params='inside'),
        sortcm,
        menus.ContextCommand('Delete empty directories', python=main_del_empty_dirs),
        menus.ContextCommand('Enable dry run', python=set_dry_run, params='True'),
        menus.ContextCommand('Disable dry run', python=set_dry_run, params='False')
    ])

    bgcm.compile()

    print("Context Menu added")
