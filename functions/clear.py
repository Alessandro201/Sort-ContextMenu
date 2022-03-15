from context_menu import menus


def clear():
    try:
        menus.removeMenu('SORT', type='DIRECTORY')
        menus.removeMenu('SORT', type='DIRECTORY_BACKGROUND')
        menus.removeMenu('SORT', type='FILES')

    except:
        pass
