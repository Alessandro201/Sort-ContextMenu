from context_menu import menus

from functions.basefunctions import clear_menus
from functions.Extract import extract_all_inside, extract_all_outside
from functions.Delete import del_empty_dirs
from functions.Sort import *

if __name__ == '__main__':
    # CLEAR PREVIOUS MENUS
    clear_menus()
    print("Previous context menu cleaned")

    # SORT CONTEXT MENU
    sortcm = menus.ContextMenu("Sort by date")

    sortcm.add_items([menus.ContextCommand('Modification date yyyy/mm/dd', python=sort_by_modification_date_ymd),
                      menus.ContextCommand('Modification date yyyy/mm', python=sort_by_modification_date_ym),
                      menus.ContextCommand('Modification date yyyy', python=sort_by_modification_date_y),
                      menus.ContextCommand('Acquisition date yyyy/mm/dd', python=sort_by_acquisition_date_ymd),
                      menus.ContextCommand('Acquisition date yyyy/mm', python=sort_by_acquisition_date_ym),
                      menus.ContextCommand('Acquisition date yyyy', python=sort_by_acquisition_date_y),
                      menus.ContextCommand('Media Creation date yyyy/mm/dd',python=sort_by_win_media_creation_date_ymd),
                      menus.ContextCommand('Media Creation date yyyy/mm', python=sort_by_win_media_creation_date_ym),
                      menus.ContextCommand('Media Creation date yyyy', python=sort_by_win_media_creation_date_y),
                      menus.ContextCommand('Date written in the name yyyy/mm/dd', python=sort_by_date_in_name_ymd),
                      menus.ContextCommand('Date written in the name yyyy/mm', python=sort_by_date_in_name_ym),
                      menus.ContextCommand('Date written in the name yyyy', python=sort_by_date_in_name_y),
                      ])

    # DIRECTORY CONTEXT MENU
    dircm = menus.ContextMenu('SORT', type='DIRECTORY')

    dircm.add_items([menus.ContextCommand('Extract all inside', python=extract_all_inside),
                     menus.ContextCommand('Extract all outside', python=extract_all_outside),
                     menus.ContextCommand('Sort by Extension inside', python=sort_by_ext_inside),
                     menus.ContextCommand('Sort by Extension outside', python=sort_by_ext_outside),
                     menus.ContextCommand('Sort by Type inside', python=sort_by_type_inside),
                     menus.ContextCommand('Sort by Type outside', python=sort_by_type_outside),
                     sortcm,
                     menus.ContextCommand('Delete empty directories inside', python=main_del_empty_dirs)])

    dircm.compile()

    # DIRECTORY_BACKGROUND CONTEXT MENU
    bgcm = menus.ContextMenu('SORT', type='DIRECTORY_BACKGROUND')

    bgcm.add_items([menus.ContextCommand('Extract all', python=extract_all_inside),
                    menus.ContextCommand('Sort by Extension', python=sort_by_ext_inside),
                    menus.ContextCommand('Sort by Type', python=sort_by_type_inside),
                    sortcm,
                    menus.ContextCommand('Delete empty directories', python=main_del_empty_dirs)])

    bgcm.compile()

    print("Context Menu added")
